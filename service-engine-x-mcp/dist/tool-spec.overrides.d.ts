/**
 * Manual overlays for route-only gaps and lifecycle-specific naming.
 */
export declare const manualOverlayToolNames: readonly ["serx_upsert_contact", "serx_list_orders", "serx_create_order", "serx_get_order", "serx_update_order", "serx_delete_order", "serx_mark_order_task_complete", "serx_mark_order_task_incomplete", "serx_list_invoices", "serx_create_invoice", "serx_get_invoice", "serx_update_invoice", "serx_delete_invoice", "serx_charge_invoice", "serx_mark_invoice_paid", "serx_list_tickets", "serx_create_ticket", "serx_get_ticket", "serx_update_ticket", "serx_delete_ticket"];
export declare function buildToolDriftReport(): {
    generatedCount: number;
    registeredCount: number;
    missingFromRegistered: string[];
    extraInRegistered: string[];
};
