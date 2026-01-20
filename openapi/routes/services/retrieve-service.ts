import { RouteMetadata } from "../../index";

export const openapi: RouteMetadata = {
  method: "GET",
  path: "/api/services/{id}",
  summary: "Retrieve a service",
  description: "Returns a single service by ID",
  tags: ["Services"],
  operationId: "retrieveService",
  responses: {
    "200": {
      description: "Successful response",
    },
    "401": {
      description: "Unauthorized",
    },
    "404": {
      description: "Service not found",
    },
  },
};
