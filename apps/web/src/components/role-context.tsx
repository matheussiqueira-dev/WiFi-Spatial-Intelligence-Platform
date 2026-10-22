"use client";

import { createContext, useContext } from "react";
import { allows, type Role } from "../lib/access";

// Role of the signed-in token; null while disconnected (every write control hidden).
export const RoleContext = createContext<Role | null>(null);

export function useAllows(minimum: Role): boolean {
  return allows(useContext(RoleContext), minimum);
}
