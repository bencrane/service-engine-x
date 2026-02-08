import { RouteMetadata } from "../../index";

export const openapi: RouteMetadata = {
  method: "POST",
  path: "/api/proposals",
  summary: "Create a proposal",
  description: "Creates a new draft proposal with line items. Calculates total from items automatically.",
  tags: ["Proposals"],
  operationId: "createProposal",
  responses: {
    "201": {
      description: "Proposal created successfully",
    },
    "400": {
      description: "Validation error - invalid input data",
    },
    "401": {
      description: "Unauthorized - invalid or missing API token",
    },
    "422": {
      description: "Unprocessable entity - referenced service does not exist",
    },
  },
};
