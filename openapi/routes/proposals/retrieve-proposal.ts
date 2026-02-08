import { RouteMetadata } from "../../index";

export const openapi: RouteMetadata = {
  method: "GET",
  path: "/api/proposals/{id}",
  summary: "Retrieve a proposal",
  description: "Returns a single proposal with its line items",
  tags: ["Proposals"],
  operationId: "retrieveProposal",
  responses: {
    "200": {
      description: "Successful response with proposal details",
    },
    "401": {
      description: "Unauthorized - invalid or missing API token",
    },
    "404": {
      description: "Proposal not found",
    },
  },
};
