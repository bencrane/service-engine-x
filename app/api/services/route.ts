import { NextRequest } from "next/server";
import { listServices } from "./list-services";
import { createService } from "./create-service";

export async function GET(request: NextRequest) {
  return listServices(request);
}

export async function POST(request: NextRequest) {
  return createService(request);
}
