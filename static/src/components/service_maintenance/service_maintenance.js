/** @odoo-module */
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Card } from "../card/card";

const { Component, useState, onMounted } = owl;

export class service_maintenance extends Component {
    setup() {
        const notificationService = useService("notification");
        const ormService = useService("orm");
        const actionService = useService("action");

        if (!notificationService || !ormService || !actionService) {
            throw new Error("Required services are not properly initialized.");
        }

        this.orm = ormService;
        this.actionService = actionService;

        this.state = useState({
            from_date: null,
            to_date: null,
            service_type_counts: {
                vehicle: 0,
                cart: 0,
                machine: 0,
                fertilizer: 0,
            },
            payment_counts: {
                draft: 0,
                posted: 0,
            },
        });

        onMounted(() => {
            this.updateData(); // Fetch data on component mount
        });
    }

    async updateData() {
        let domain = [];
        if (this.state.from_date && this.state.to_date) {
            domain = [
                ["date", ">=", this.state.from_date],  // Change to 'date' for fuel requisitions
                ["date", "<=", this.state.to_date],    // Change to 'date' for fuel requisitions
            ];
        }

        try {
            const serviceCounts = await this.getServiceTypeCounts(domain);
            const paymentCounts = await this.getPaymentCounts(domain);

            this.state.service_type_counts = serviceCounts;
            this.state.payment_counts = paymentCounts;
        } catch (error) {
            console.error("Error while updating data:", error);
        }
    }

    async getServiceTypeCounts(baseDomain) {
        const domain = baseDomain || [];
        try {
            return {
                vehicle: await this.orm.searchCount("dsl.fuel.requisition", [...domain, ["product_service_type_id.name", "=", "Vehicle"]]),
                cart: await this.orm.searchCount("dsl.fuel.requisition", [...domain, ["product_service_type_id.name", "=", "Cart"]]),
                machine: await this.orm.searchCount("dsl.fuel.requisition", [...domain, ["product_service_type_id.name", "=", "Machine"]]),
                fertilizer: await this.orm.searchCount("dsl.fuel.requisition", [...domain, ["product_service_type_id.name", "=", "Fertilizer"]]),
            };
        } catch (error) {
            console.error("Error fetching service type counts:", error);
            return { vehicle: 0, cart: 0, machine: 0, fertilizer: 0 };
        }
    }

    async getPaymentCounts(baseDomain) {
        const domain = baseDomain || [];
        try {
            return {
                draft: await this.orm.searchCount("account.payment", [...domain, ["state", "=", "draft"]]),
                posted: await this.orm.searchCount("account.payment", [...domain, ["state", "=", "posted"]]),
            };
        } catch (error) {
            console.error("Error fetching payment counts:", error);
            return { draft: 0, posted: 0 };
        }
    }

    // Button Click Handlers for Date Filters
    async onLast7DaysClick() {
        const today = new Date();
        const last7Days = new Date(today);
        last7Days.setDate(today.getDate() - 7);

        this.state.from_date = last7Days.toISOString().split("T")[0];
        this.state.to_date = today.toISOString().split("T")[0];
        await this.updateData();
    }

    async onMonthlyClick() {
        const today = new Date();
        const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
        
        this.state.from_date = firstDayOfMonth.toISOString().split("T")[0];
        this.state.to_date = today.toISOString().split("T")[0];
        await this.updateData();
    }

    async onYearlyClick() {
        const today = new Date();
        const firstDayOfYear = new Date(today.getFullYear(), 0, 1);

        this.state.from_date = firstDayOfYear.toISOString().split("T")[0];
        this.state.to_date = today.toISOString().split("T")[0];
        await this.updateData();
    }

    async onFromDateChange(event) {
        this.state.from_date = event.target.value;
        await this.updateData();
    }

    async onToDateChange(event) {
        this.state.to_date = event.target.value;
        await this.updateData();
    }

    async onRefreshClick() {
        await this.updateData();
    }

    async onClearClick() {
        this.state.from_date = null;
        this.state.to_date = null;
        await this.updateData();
    }

    buildDateFilterDomain(baseDomain = []) {
        const domain = [...baseDomain];
        
        if (this.state.from_date) {
            domain.push(["date", ">=", this.state.from_date]);  // Change to 'date' for fuel requisitions
        }
        
        if (this.state.to_date) {
            domain.push(["date", "<=", this.state.to_date]);    // Change to 'date' for fuel requisitions
        }

        return domain;
    }

    // Function for displaying records based on type
    async showVehicleRecords() {
        const domain = this.buildDateFilterDomain([["product_service_type_id.name", "=", "Vehicle"]]);
        console.log("Vehicle Records Domain:", domain); // Debugging line
        await this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Vehicle Records",
            res_model: "dsl.fuel.requisition",
            domain: domain,
            views: [
                [false, "list"],
                [false, "form"],
            ],
        });
    }

    async showCartRecords() {
        const domain = this.buildDateFilterDomain([["product_service_type_id.name", "=", "Cart"]]);
        console.log("Cart Records Domain:", domain); // Debugging line
        await this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Cart Records",
            res_model: "dsl.fuel.requisition",
            domain: domain,
            views: [
                [false, "list"],
                [false, "form"],
            ],
        });
    }

    async showMachineRecords() {
        const domain = this.buildDateFilterDomain([["product_service_type_id.name", "=", "Machine"]]);
        console.log("Machine Records Domain:", domain); // Debugging line
        await this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Machine Records",
            res_model: "dsl.fuel.requisition",
            domain: domain,
            views: [
                [false, "list"],
                [false, "form"],
            ],
        });
    }

    async showFertilizerRecords() {
        const domain = this.buildDateFilterDomain([["product_service_type_id.name", "=", "Fertilizer"]]);
        console.log("Fertilizer Records Domain:", domain); // Debugging line
        await this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Fertilizer Records",
            res_model: "dsl.fuel.requisition",
            domain: domain,
            views: [
                [false, "list"],
                [false, "form"],
            ],
        });
    }

    async showDraftPayments() {
        const domain = this.buildDateFilterDomain([["state", "=", "draft"]]);
        console.log("Draft Payments Domain:", domain); // Debugging line
        await this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Draft Payments",
            res_model: "account.payment",
            domain: domain,
            views: [
                [false, "list"],
                [false, "form"],
            ],
        });
    }

    async showPostedPayments() {
        const domain = this.buildDateFilterDomain([["state", "=", "posted"]]);
        console.log("Posted Payments Domain:", domain); // Debugging line
        await this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Posted Payments",
            res_model: "account.payment",
            domain: domain,
            views: [
                [false, "list"],
                [false, "form"],
            ],
        });
    }
}

service_maintenance.template = "dsl_service_maintenance.service_maintenance";
service_maintenance.components = { Card };
registry.category("actions").add("dsl_service_maintenance.service_maintenance", service_maintenance);
