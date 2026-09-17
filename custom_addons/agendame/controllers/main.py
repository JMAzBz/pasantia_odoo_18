import datetime
import json

import pytz
from odoo import fields, http
from odoo.http import request


class AppointmentController(http.Controller):
    @http.route("/agendame", type="http", auth="public", website=True)
    def appointment_index(self, **kwargs):
        domain = [("active", "=", True)]
        # Authenticated internal users see only their own agendas
        # (Odoo record rules enforce this). Public visitors see all.
        if request.env.user.has_group("base.group_user"):
            appointment_types = request.env["agendame.type"].search(domain)
        else:
            appointment_types = request.env["agendame.type"].sudo().search(domain)
        return request.render(
            "agendame.appointments_list",
            {
                "appointment_types": appointment_types,
            },
        )

    @http.route(
        "/agendame/<int:agendame_type_id>",
        type="http",
        auth="public",
        website=True,
    )
    def appointment_page(self, agendame_type_id, **kwargs):
        # 1. Respetar el contexto del usuario (con o sin sudo)
        if request.env.user.has_group("base.group_user"):
            appointment_type = request.env["agendame.type"].browse(agendame_type_id)
        else:
            appointment_type = (
                request.env["agendame.type"].sudo().browse(agendame_type_id)
            )

        if not appointment_type.exists():
            return request.not_found()

        # 2. FILTRADO CORRECTO DEL PERSONAL:
        # Si es usuario interno, solo ve SU propio usuario dentro del staff asignado.
        # Si es visitante público, ve ÚNICAMENTE los usuarios asignados explícitamente en `staff_user_ids`.
        if request.env.user.has_group("base.group_user"):
            staff_records = appointment_type.staff_user_ids.filtered(
                lambda u: u.id == request.env.user.id
            )
        else:
            staff_records = appointment_type.sudo().staff_user_ids

        # (Se eliminó el fallback que forzaba a create_uid o request.env.user)

        staff_users = []
        for user in staff_records:
            staff_users.append({
                "id": user.id,
                "name": user.name,
                "image_url": f"/web/image/res.users/{user.id}/image_128",
            })

        # Preparamos lista de países Latam
        latam_codes = ["CL", "AR", "MX", "CO", "PE", "VE", "EC", "BO", "UY", "PY", "BR"]
        countries = (
            request.env["res.country"].sudo().search([("code", "in", latam_codes)])
        )
        countries = sorted(countries, key=lambda c: 0 if c.code == "CL" else 1)

        return request.render(
            "agendame.appointment_details",
            {
                "appointment_type": appointment_type,
                "staff_users": staff_users,
                "countries": countries,
                "days_es": {
                    "Mon": "Lun",
                    "Tue": "Mar",
                    "Wed": "Mié",
                    "Thu": "Jue",
                    "Fri": "Vie",
                    "Sat": "Sáb",
                    "Sun": "Dom",
                },
                "months_es": {
                    "January": "Enero",
                    "February": "Febrero",
                    "March": "Marzo",
                    "April": "Abril",
                    "May": "Mayo",
                    "June": "Junio",
                    "July": "Julio",
                    "August": "Agosto",
                    "September": "Septiembre",
                    "October": "Octubre",
                    "November": "Noviembre",
                    "December": "Diciembre",
                },
            },
        )

    @http.route(
        "/agendame/<int:agendame_type_id>/slots",
        type="http",
        auth="public",
        website=True,
        csrf=False,
    )
    def appointment_slots_json(self, agendame_type_id, staff_user_id=None, **kwargs):
        """Return available slots for a specific staff user as JSON."""
        appointment_type = (
            request.env["agendame.type"].sudo().browse(agendame_type_id)
        )
        if not appointment_type.exists() or not appointment_type.active:
            return request.make_json_response({"error": "not_found"}, status=404)

        if not staff_user_id:
            return request.make_json_response(
                {"error": "missing_staff_user_id"}, status=400
            )

        try:
            staff_user_id = int(staff_user_id)
        except (TypeError, ValueError):
            return request.make_json_response(
                {"error": "invalid_staff_user_id"}, status=400
            )

        # Validar estrictamente que el usuario pertenezca a la lista del staff de la agenda
        staff_user = appointment_type.sudo().staff_user_ids.filtered(
            lambda u: u.id == staff_user_id
        )
        if not staff_user:
            return request.make_json_response(
                {"error": "staff_user_not_found"}, status=404
            )

        slots = appointment_type._get_appointment_slots_for_staff(staff_user)
        appt_tz = pytz.timezone(appointment_type.appointment_tz or "UTC")

        # Group by date
        grouped = {}
        for slot in slots:
            slot_localized = pytz.utc.localize(slot).astimezone(appt_tz)
            date_key = slot_localized.strftime("%Y-%m-%d")
            if date_key not in grouped:
                grouped[date_key] = {
                    "date": date_key,
                    "weekday": slot_localized.strftime("%a"),
                    "day": slot_localized.strftime("%d"),
                    "month": slot_localized.strftime("%B"),
                    "slots": [],
                }
            grouped[date_key]["slots"].append({
                "time": slot_localized.strftime("%H:%M"),
                "datetime": slot_localized.strftime("%Y-%m-%d %H:%M:%S"),
            })

        return request.make_json_response({
            "dates": list(grouped.values()),
        })

    @http.route(
        "/agendame/submit",
        type="http",
        auth="public",
        methods=["POST"],
        website=True,
        csrf=True,
    )
    def appointment_submit(self, **post):
        # --- Defensive input validation ---
        def _int_or_none(raw):
            try:
                return int(str(raw).strip())
            except (TypeError, ValueError):
                return None

        agendame_type_id = _int_or_none(post.get("agendame_type_id"))
        if not agendame_type_id:
            return request.redirect("/agendame?error=invalid_type")

        staff_user_id = _int_or_none(post.get("staff_user_id"))
        if not staff_user_id:
            return request.redirect(
                f"/agendame/{agendame_type_id}?error=missing_staff"
            )

        name = (post.get("name") or "").strip()
        if not name:
            return request.redirect(f"/agendame/{agendame_type_id}?error=missing_name")

        email = (post.get("email") or "").strip()
        if not email:
            return request.redirect(f"/agendame/{agendame_type_id}?error=missing_email")

        country_id = False
        raw_country_id = (post.get("country_id") or "").strip()
        if raw_country_id:
            country_id = _int_or_none(raw_country_id)
            if not country_id or not (
                request.env["res.country"].sudo().browse(country_id).exists()
            ):
                return request.redirect(
                    f"/agendame/{agendame_type_id}?error=invalid_country"
                )

        phone = (post.get("phone") or "").strip()

        date_str = (post.get("date") or "").strip()
        if not date_str:
            return request.redirect(f"/agendame/{agendame_type_id}?error=no_date")

        appointment_type = request.env["agendame.type"].sudo().browse(agendame_type_id)
        if not appointment_type.exists():
            return request.not_found()
        if not appointment_type.active:
            return request.not_found()

        # Validación estricta del staff en el submit
        staff_user = appointment_type.sudo().staff_user_ids.filtered(
            lambda u: u.id == staff_user_id
        )
        if not staff_user:
            return request.redirect(
                f"/agendame/{agendame_type_id}?error=invalid_staff"
            )

        # Convert submitted date back to UTC
        appt_tz = pytz.timezone(appointment_type.appointment_tz or "UTC")
        try:
            local_start = appt_tz.localize(
                datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            )
        except ValueError:
            return request.redirect(f"/agendame/{agendame_type_id}?error=invalid_date")
        utc_start = local_start.astimezone(pytz.UTC).replace(tzinfo=None)

        duration = appointment_type.appointment_duration
        utc_end = utc_start + datetime.timedelta(hours=duration)

        if utc_start <= fields.Datetime.now():
            return request.redirect(f"/agendame/{agendame_type_id}?error=past_slot")

        # Validate the slot is in the offered grid
        if not appointment_type._is_offered_slot(utc_start):
            return request.redirect(f"/agendame/{agendame_type_id}?error=invalid_slot")

        # --- RACE CONDITION PROTECTION (TOCTOU) ---
        request.env.cr.execute(
            "SELECT id FROM agendame_type WHERE id = %s FOR UPDATE",
            [appointment_type.id],
        )
        # Re-verify availability for the SPECIFIC staff user
        if not appointment_type._is_slot_available_for_staff(
            staff_user, utc_start, utc_end
        ):
            return request.redirect(
                f"/agendame/{agendame_type_id}?error=already_booked"
            )

        # Create partner if doesn't exist
        partner = (
            request.env["res.partner"].sudo().search([("email", "=", email)], limit=1)
        )
        if not partner:
            partner = (
                request.env["res.partner"]
                .sudo()
                .create(
                    {
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "country_id": country_id,
                    }
                )
            )
        else:
            vals = {}
            if not partner.phone:
                vals["phone"] = phone
            if not partner.country_id:
                vals["country_id"] = country_id
            if vals:
                partner.write(vals)

        # Create calendar event with ONLY the selected professional
        partner_ids = [(4, partner.id)]
        if staff_user.partner_id:
            partner_ids.append((4, staff_user.partner_id.id))

        event = (
            request.env["calendar.event"]
            .sudo()
            .create(
                {
                    "name": f"{appointment_type.name}: {name}",
                    "start": utc_start,
                    "stop": utc_end,
                    "user_id": staff_user.id,
                    "partner_ids": partner_ids,
                    "agendame_type_id": appointment_type.id,
                    "agendame_status": "booked",
                    "videocall_source": appointment_type.event_videocall_source,
                    "client_country_id": country_id,
                }
            )
        )

        return request.render(
            "agendame.appointment_thanks",
            {
                "event": event,
            },
        )