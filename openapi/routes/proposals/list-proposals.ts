import { RouteMetadata } from "../../index";

export const openapi: RouteMetadata = {
  method: "GET",
  path: "/api/proposals",
  summary: "List all proposals",
  description: "Returns a paginated list of proposals for the authenticated organization",
  tags: ["Proposals"],
  operationId: "listProposals",
  responses: {
    "200": {
      description: "Successful response with paginated proposals",
    },
    "401": {
      description: "Unauthorized - invalid or missing API token",
    },
  },
};
