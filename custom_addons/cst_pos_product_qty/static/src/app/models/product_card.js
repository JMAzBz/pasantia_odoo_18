/** @odoo-module **/

import { ProductCard } from "@point_of_sale/app/components/product_card/product_card";
import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/hooks/pos_hook";

patch(ProductCard.prototype, {
    setup() {
        super.setup();
        this.pos = usePos();
    },
    get availableQty() {
        const productTemplate = this.props.product;
        if (!productTemplate || productTemplate.type !== "consu") {
            return null;
        }

        let totalQty = 0;
        for (const variant of productTemplate.product_variant_ids || []) {
            totalQty += variant.qty_available || 0;
        }
        //Prevent overflow when stock becomes 1000+
        if (totalQty > 999) {
            return "999+";
        }

        return totalQty;
    },
});
