# Known Issues

## TypeScript Errors

### create-invoice.ts:156 - Type conversion error

**File:** `app/api/invoices/create-invoice.ts`
**Line:** 156

**Error:**
```
Type error: Conversion of type 'any[]' to type 'Record<string, unknown>' may be a mistake because neither type sufficiently overlaps with the other.
```

**Cause:** `client.addresses` is returned as an array from Supabase join, but code casts it to a single Record.

**Fix:** Should use `addressArray[0]` or handle the array properly.
