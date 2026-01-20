/**
 * Shared OpenAPI schemas
 */

export const schemas = {
  Address: {
    type: "object",
    properties: {
      line_1: { type: "string", description: "Address line 1" },
      line_2: { type: "string", description: "Address line 2" },
      city: { type: "string", description: "City" },
      state: { type: "string", description: "State/Province" },
      country: { type: "string", description: "Country code" },
      postcode: { type: "string", description: "Postal code" },
      name_f: { type: "string", description: "First name" },
      name_l: { type: "string", description: "Last name" },
      tax_id: { type: "string", description: "Tax ID" },
      company_name: { type: "string", description: "Company name" },
      company_vat: { type: "string", description: "Company VAT" },
    },
  },

  Role: {
    type: "object",
    properties: {
      id: { type: "integer", description: "Role ID" },
      name: { type: "string", description: "Role name" },
      dashboard_access: { type: "integer", description: "Dashboard access level (0-3)" },
      order_access: { type: "integer", description: "Order read access (0-3)" },
      order_management: { type: "integer", description: "Order write access (0-3)" },
      ticket_access: { type: "integer", description: "Ticket read access (0-3)" },
      ticket_management: { type: "integer", description: "Ticket write access (0-3)" },
    },
  },

  UserManager: {
    type: "object",
    properties: {
      id: { type: "integer", description: "Manager user ID" },
      name: { type: "string", description: "Manager name" },
      email: { type: "string", description: "Manager email" },
    },
  },

  Client: {
    type: "object",
    properties: {
      id: { type: "integer", description: "User ID" },
      name: { type: "string", description: "Full name" },
      name_f: { type: "string", description: "First name" },
      name_l: { type: "string", description: "Last name" },
      email: { type: "string", format: "email", description: "Email address" },
      company: { type: "string", description: "Company name" },
      tax_id: { type: "string", description: "Tax ID" },
      phone: { type: "string", description: "Phone number" },
      address: { $ref: "#/components/schemas/Address" },
      note: { type: "string", description: "Internal note" },
      balance: { type: "number", description: "Account balance" },
      spent: { type: "string", description: "Total spent" },
      optin: { type: "string", description: "Marketing consent" },
      stripe_id: { type: "string", description: "Stripe customer ID" },
      custom_fields: { type: "object", description: "Custom field data" },
      status: { type: "integer", description: "Account status" },
      role_id: { type: "integer", description: "Role ID" },
      role: { $ref: "#/components/schemas/Role" },
      aff_id: { type: "integer", description: "Affiliate ID" },
      aff_link: { type: "string", description: "Affiliate link" },
      ga_cid: { type: "string", description: "Google Analytics client ID" },
      employee_id: { type: "integer", description: "Assigned employee ID" },
      managers: {
        type: "array",
        items: { $ref: "#/components/schemas/UserManager" },
        description: "Assigned managers",
      },
      team_owner_ids: {
        type: "array",
        items: { type: "integer" },
        description: "Team owner IDs",
      },
      team_member_ids: {
        type: "array",
        items: { type: "integer" },
        description: "Team member IDs",
      },
      created_at: {
        type: "string",
        format: "date-time",
        description: "Created timestamp",
      },
    },
    required: ["id", "name", "name_f", "name_l", "email"],
  },

  PaginationLinks: {
    type: "object",
    properties: {
      first: { type: "string", description: "URL to first page" },
      last: { type: "string", description: "URL to last page" },
      prev: { type: "string", nullable: true, description: "URL to previous page" },
      next: { type: "string", nullable: true, description: "URL to next page" },
    },
  },

  PaginationMeta: {
    type: "object",
    properties: {
      current_page: { type: "integer", description: "Current page number" },
      from: { type: "integer", description: "First item index on page" },
      last_page: { type: "integer", description: "Last page number" },
      path: { type: "string", description: "Base URL path" },
      per_page: { type: "integer", description: "Items per page" },
      to: { type: "integer", description: "Last item index on page" },
      total: { type: "integer", description: "Total items" },
    },
  },
};
