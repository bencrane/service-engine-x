# FastAPI Migration Plan

Excellent. Based on my analysis, here's the comprehensive migration plan:     
                                                                                
  ---                                                                           
  FastAPI Migration Plan for Service-Engine-X                                   
                                                                                
  1. Recommended Project Structure                                              
                                                                                
  service-engine-x-api/                                                         
  ├── app/                                                                      
  │   ├── __init__.py                                                           
  │   ├── main.py                    # FastAPI app, middleware, startup         
  │   ├── config.py                  # Environment variables, settings          
  │   ├── database.py                # Supabase client initialization           
  │   │                                                                         
  │   ├── auth/                                                                 
  │   │   ├── __init__.py                                                       
  │   │   ├── dependencies.py        # get_current_org, require_auth            
  │   │   └── utils.py               # hash_token, extract_bearer_token         
  │   │                                                                         
  │   ├── models/                                                               
  │   │   ├── __init__.py                                                       
  │   │   ├── common.py              # PaginatedResponse, ValidationError       
  │   │   ├── clients.py             # Client request/response models           
  │   │   ├── services.py                                                       
  │   │   ├── orders.py                                                         
  │   │   ├── proposals.py                                                      
  │   │   ├── invoices.py                                                       
  │   │   └── tickets.py                                                        
  │   │                                                                         
  │   ├── routers/                                                              
  │   │   ├── __init__.py                                                       
  │   │   ├── health.py              # /api/health                              
  │   │   ├── clients.py             # /api/clients/*                           
  │   │   ├── services.py            # /api/services/*                          
  │   │   ├── orders.py              # /api/orders/*                            
  │   │   ├── order_tasks.py         # /api/order-tasks/*                       
  │   │   ├── order_messages.py      # /api/order-messages/*                    
  │   │   ├── proposals.py           # /api/proposals/*                         
  │   │   ├── invoices.py            # /api/invoices/*                          
  │   │   └── tickets.py             # /api/tickets/*                           
  │   │                                                                         
  │   ├── services/                  # Business logic layer                     
  │   │   ├── __init__.py                                                       
  │   │   ├── clients.py                                                        
  │   │   ├── services.py                                                       
  │   │   ├── orders.py                                                         
  │   │   ├── proposals.py                                                      
  │   │   └── invoices.py                                                       
  │   │                                                                         
  │   └── utils/                                                                
  │       ├── __init__.py                                                       
  │       ├── pagination.py          # build_pagination_response                
  │       ├── validation.py          # validate_uuid, validate_email            
  │       └── serializers.py         # Common serialization helpers             
  │                                                                             
  ├── tests/                                                                    
  │   ├── __init__.py                                                           
  │   ├── conftest.py                # Pytest fixtures                          
  │   ├── test_auth.py                                                          
  │   ├── test_clients.py                                                       
  │   └── ...                                                                   
  │                                                                             
  ├── requirements.txt                                                          
  ├── pyproject.toml                                                            
  ├── Dockerfile                                                                
  ├── docker-compose.yml                                                        
  └── .env.example                                                              
                                                                                
  ---                                                                           
  2. Python Dependencies                                                        
                                                                                
  # requirements.txt                                                            
                                                                                
  # Core Framework                                                              
  fastapi==0.109.2                                                              
  uvicorn[standard]==0.27.1                                                     
  pydantic==2.6.1                                                               
  pydantic-settings==2.1.0                                                      
                                                                                
  # Database                                                                    
  supabase==2.3.4                                                               
  postgrest-py==0.13.0                                                          
                                                                                
  # Authentication                                                              
  python-jose[cryptography]==3.3.0    # JWT if needed later                     
  passlib[bcrypt]==1.7.4              # Password hashing (bcrypt)               
                                                                                
  # Utilities                                                                   
  python-multipart==0.0.9             # Form data handling                      
  httpx==0.26.0                       # Async HTTP client                       
  python-dotenv==1.0.1                # Environment variables                   
                                                                                
  # Development                                                                 
  pytest==8.0.0                                                                 
  pytest-asyncio==0.23.4                                                        
  pytest-cov==4.1.0                                                             
  black==24.1.1                                                                 
  ruff==0.2.1                                                                   
  mypy==1.8.0                                                                   
                                                                                
  ---                                                                           
  3. Migration Strategy (Recommended Order)                                     
                                                                                
  Phase 1: Foundation (Day 1)                                                   
  1. Project setup, dependencies, Docker config                                 
  2. config.py - Environment variables                                          
  3. database.py - Supabase client                                              
  4. auth/ - Authentication (critical path)                                     
  5. models/common.py - Shared response models                                  
  6. routers/health.py - Verify everything works                                
                                                                                
  Phase 2: Core CRUD Endpoints (Days 2-3)                                       
  7. clients/ - Full CRUD (template for others)                                 
  8. services/ - Similar pattern, simpler model                                 
  9. orders/ - More complex with relations                                      
                                                                                
  Phase 3: Nested Resources (Day 4)                                             
  10. orders/{id}/tasks/ - Nested under orders                                  
  11. orders/{id}/messages/ - Nested under orders                               
  12. order-tasks/{id}/ - Standalone task operations                            
  13. order-messages/{id}/ - Standalone message operations                      
                                                                                
  Phase 4: Complex Workflows (Day 5)                                            
  14. proposals/ - Including send/sign workflows                                
  15. invoices/ - Including charge/mark_paid                                    
                                                                                
  Phase 5: Remaining & Polish (Day 6)                                           
  16. tickets/ - Final domain                                                   
  17. API index endpoint                                                        
  18. OpenAPI customization                                                     
  19. Error handling refinement                                                 
  20. Testing & validation                                                      
                                                                                
  ---                                                                           
  4. Key Implementation Patterns                                                
                                                                                
  Authentication Dependency:                                                    
  # app/auth/dependencies.py                                                    
  from fastapi import Depends, HTTPException, Header                            
  from hashlib import sha256                                                    
  from app.database import supabase                                             
                                                                                
  async def get_current_org(                                                    
      authorization: str = Header(None)                                         
  ) -> dict:                                                                    
      if not authorization or not authorization.startswith("Bearer "):          
          raise HTTPException(status_code=401, detail="Unauthorized")           
                                                                                
      token = authorization[7:]  # Remove "Bearer "                             
      token_hash = sha256(token.encode()).hexdigest()                           
                                                                                
      result = supabase.table("api_tokens") \                                   
          .select("id, user_id, org_id, expires_at") \                          
          .eq("token_hash", token_hash) \                                       
          .single() \                                                           
          .execute()                                                            
                                                                                
      if not result.data:                                                       
          raise HTTPException(status_code=401, detail="Unauthorized")           
                                                                                
      # Check expiration, update last_used_at...                                
      return {"org_id": result.data["org_id"], "user_id":                       
  result.data["user_id"]}                                                       
                                                                                
  Pagination Response Model:                                                    
  # app/models/common.py                                                        
  from pydantic import BaseModel                                                
  from typing import Generic, TypeVar, List, Optional                           
                                                                                
  T = TypeVar("T")                                                              
                                                                                
  class PaginationLinks(BaseModel):                                             
      first: str                                                                
      last: str                                                                 
      prev: Optional[str]                                                       
      next: Optional[str]                                                       
                                                                                
  class PaginationMeta(BaseModel):                                              
      current_page: int                                                         
      from_: int = Field(alias="from")                                          
      to: int                                                                   
      last_page: int                                                            
      per_page: int                                                             
      total: int                                                                
      path: str                                                                 
                                                                                
  class PaginatedResponse(BaseModel, Generic[T]):                               
      data: List[T]                                                             
      links: PaginationLinks                                                    
      meta: PaginationMeta                                                      
                                                                                
  Router Pattern:                                                               
  # app/routers/clients.py                                                      
  from fastapi import APIRouter, Depends, Query                                 
  from app.auth.dependencies import get_current_org                             
                                                                                
  router = APIRouter(prefix="/api/clients", tags=["Clients"])                   
                                                                                
  @router.get("", response_model=PaginatedResponse[ClientResponse])             
  async def list_clients(                                                       
      auth: dict = Depends(get_current_org),                                    
      limit: int = Query(20, ge=1, le=100),                                     
      page: int = Query(1, ge=1),                                               
      sort: str = Query("created_at:desc")                                      
  ):                                                                            
      # Implementation                                                          
      pass                                                                      
                                                                                
  ---                                                                           
  5. Breaking Changes & Differences                                             
  ┌────────────┬───────────────────────┬───────────────────┬──────────────────┐ 
  │   Aspect   │        Next.js        │      FastAPI      │      Impact      │ 
  ├────────────┼───────────────────────┼───────────────────┼──────────────────┤ 
  │            │ Mixed (some async,    │ All async         │ Low -            │ 
  │ Async      │ some sync)            │ recommended       │ supabase-py      │ 
  │            │                       │                   │ supports both    │ 
  ├────────────┼───────────────────────┼───────────────────┼──────────────────┤ 
  │ Validation │ Manual in each        │ Pydantic          │ Better - less    │ 
  │            │ handler               │ automatic         │ code, type-safe  │ 
  ├────────────┼───────────────────────┼───────────────────┼──────────────────┤ 
  │ Error      │ { message, errors }   │ Default: { detail │ Must customize   │ 
  │ Format     │                       │  }                │ error handler    │ 
  ├────────────┼───────────────────────┼───────────────────┼──────────────────┤ 
  │ Path       │ [id] folder           │ {id} in route     │ None - just      │ 
  │ Params     │ convention            │ decorator         │ syntax           │ 
  ├────────────┼───────────────────────┼───────────────────┼──────────────────┤ 
  │ Query      │ Manual                │ Query() with      │ Better -         │ 
  │ Params     │ searchParams.get()    │ validation        │ automatic type   │ 
  │            │                       │                   │ coercion         │ 
  ├────────────┼───────────────────────┼───────────────────┼──────────────────┤ 
  │ OpenAPI    │ Manual metadata files │ Auto-generated    │ Better - less    │ 
  │            │                       │ from types        │ maintenance      │ 
  ├────────────┼───────────────────────┼───────────────────┼──────────────────┤ 
  │ Response   │ NextResponse.json()   │ Return dict/model │ Simpler          │ 
  ├────────────┼───────────────────────┼───────────────────┼──────────────────┤ 
  │ Status     │ Manual { status: 201  │ status_code=201   │ Same             │ 
  │ Codes      │ }                     │ param             │                  │ 
  └────────────┴───────────────────────┴───────────────────┴──────────────────┘ 
  Required Custom Error Handler:                                                
  # To match Next.js validation error format                                    
  @app.exception_handler(RequestValidationError)                                
  async def validation_exception_handler(request, exc):                         
      errors = {}                                                               
      for error in exc.errors():                                                
          field = ".".join(str(loc) for loc in error["loc"][1:])                
          if field not in errors:                                               
              errors[field] = []                                                
          errors[field].append(error["msg"])                                    
                                                                                
      return JSONResponse(                                                      
          status_code=400,                                                      
          content={"message": "The given data was invalid.", "errors": errors}  
      )                                                                         
                                                                                
  ---                                                                           
  6. Complexity & Effort Estimate                                               
  ┌───────────────────────────────┬───────────┬────────────┬──────────────────┐ 
  │           Component           │ Endpoints │ Complexity │ Estimated Effort │ 
  ├───────────────────────────────┼───────────┼────────────┼──────────────────┤ 
  │ Foundation (auth, db, models) │ -         │ Medium     │ 4-6 hours        │ 
  ├───────────────────────────────┼───────────┼────────────┼──────────────────┤ 
  │ Clients                       │ 5         │ Medium     │ 3-4 hours        │ 
  ├───────────────────────────────┼───────────┼────────────┼──────────────────┤ 
  │ Services                      │ 5         │ Low        │ 2-3 hours        │ 
  ├───────────────────────────────┼───────────┼────────────┼──────────────────┤ 
  │ Orders                        │ 5         │ Medium     │ 3-4 hours        │ 
  ├───────────────────────────────┼───────────┼────────────┼──────────────────┤ 
  │ Order Tasks                   │ 6         │ Medium     │ 3-4 hours        │ 
  ├───────────────────────────────┼───────────┼────────────┼──────────────────┤ 
  │ Order Messages                │ 3         │ Low        │ 1-2 hours        │ 
  ├───────────────────────────────┼───────────┼────────────┼──────────────────┤ 
  │ Proposals                     │ 5         │ High       │ 4-5 hours        │ 
  ├───────────────────────────────┼───────────┼────────────┼──────────────────┤ 
  │ Invoices                      │ 7         │ High       │ 5-6 hours        │ 
  ├───────────────────────────────┼───────────┼────────────┼──────────────────┤ 
  │ Tickets                       │ 5         │ Low        │ 2-3 hours        │ 
  ├───────────────────────────────┼───────────┼────────────┼──────────────────┤ 
  │ Testing & Polish              │ -         │ Medium     │ 4-6 hours        │ 
  └───────────────────────────────┴───────────┴────────────┴──────────────────┘ 
  Total Estimate: 32-43 hours (4-6 days)                                        
                                                                                
  ---                                                                           
  7. Risk Areas                                                                 
                                                                                
  1. Supabase-py Differences - Query builder syntax differs slightly from JS    
  client                                                                        
  2. Nested Selects - select("*, address:addresses(*)") may need different      
  syntax                                                                        
  3. Transaction Handling - No native transactions; must handle rollback        
  manually                                                                      
  4. Date/Time Handling - Ensure consistent ISO format between Python and       
  existing data                                                                 
  5. Decimal Precision - Price fields need careful Decimal handling             
                                                                                
  ---                                                                           
  8. Recommendations                                                            
                                                                                
  1. Start with Clients API - It's the most complete reference implementation   
  2. Build a test client - Validate response shapes match exactly               
  3. **Use Pydantic Field(alias=...)** - For fields like from` that are Python  
  reserved words                                                                
  4. Keep status maps in constants - Same numeric IDs mapped to same strings    
  5. Run both APIs in parallel - Compare responses during migration             
                                                                                
