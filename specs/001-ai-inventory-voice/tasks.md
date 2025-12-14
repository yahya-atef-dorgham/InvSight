# Tasks: AI-Powered Inventory Management System with Voice Interaction

**Input**: Design documents from `/specs/001-ai-inventory-voice/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: TDD is mandatory per Constitution (Test-First Development). All implementation tasks must have corresponding test tasks written first.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., [US1], [US2], [US3])
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`
- **AI Service**: `ai-service/src/`, `ai-service/tests/`
- **Voice Service**: `voice-service/src/`, `voice-service/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create backend project structure in backend/
- [X] T002 Create frontend project structure in frontend/
- [X] T003 Create ai-service project structure in ai-service/
- [X] T004 Create voice-service project structure in voice-service/
- [X] T005 Initialize backend Python project with FastAPI dependencies in backend/requirements.txt
- [X] T006 Initialize frontend React TypeScript project in frontend/package.json
- [X] T007 Initialize ai-service Python project in ai-service/requirements.txt
- [X] T008 Initialize voice-service Python project in voice-service/requirements.txt
- [X] T009 [P] Configure Python linting (ruff) and formatting (black) in backend/
- [X] T010 [P] Configure TypeScript linting (ESLint) and formatting (Prettier) in frontend/
- [X] T011 [P] Setup Docker Compose for local development in docker-compose.yml
- [X] T012 [P] Configure environment variable management in backend/src/config/settings.py
- [X] T013 [P] Configure environment variable management in frontend/.env

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Setup

- [X] T014 Setup PostgreSQL database and connection in backend/src/database/session.py
- [X] T015 Initialize Alembic migrations framework in backend/alembic.ini
- [X] T016 Configure Alembic environment in backend/alembic/env.py
- [X] T017 Create base model with tenant_id in backend/src/models/base.py
- [X] T018 Create database migration for base schema structure in backend/alembic/versions/

### Authentication & Authorization

- [X] T019 [P] Implement JWT token generation and validation in backend/src/api/middleware/auth.py
- [X] T020 [P] Implement authentication dependency injection in backend/src/api/middleware/auth.py
- [X] T021 [P] Implement tenant resolution middleware in backend/src/api/middleware/tenant.py
- [X] T022 [P] Implement RBAC permission checking in backend/src/api/middleware/permissions.py
- [X] T023 [P] Implement login endpoint in backend/src/api/v1/auth.py
- [X] T024 [P] Create frontend authentication service in frontend/src/services/auth.ts
- [X] T025 [P] Create frontend authentication context/provider in frontend/src/contexts/AuthContext.tsx
- [X] T026 [P] Create login page in frontend/src/pages/Login/Login.tsx

### API Infrastructure

- [X] T027 Setup FastAPI application with CORS in backend/src/main.py
- [X] T028 Setup API versioning structure in backend/src/api/v1/
- [X] T029 Configure error handling middleware in backend/src/api/middleware/errors.py
- [X] T030 Configure request logging middleware in backend/src/api/middleware/logging.py
- [X] T031 Setup OpenAPI documentation in backend/src/main.py

### Audit & Logging

- [X] T032 Create audit log model in backend/src/models/audit_log.py
- [X] T033 Create audit service in backend/src/services/audit_service.py
- [X] T034 Implement audit logging decorator/middleware in backend/src/api/middleware/audit.py
- [X] T035 Setup structured logging configuration in backend/src/config/logging.py

### Frontend Infrastructure

- [X] T036 [P] Setup React Router in frontend/src/App.tsx
- [X] T037 [P] Create base layout component with navigation in frontend/src/components/layout/BaseLayout.tsx
- [X] T038 [P] Create API client with interceptors in frontend/src/services/api.ts
- [X] T039 [P] Setup state management (React Query or Redux) in frontend/src/stores/
- [X] T040 [P] Create common error boundary component in frontend/src/components/common/ErrorBoundary.tsx
- [X] T041 [P] Create toast notification component in frontend/src/components/common/Toast.tsx

### Multi-Tenancy

- [X] T042 Configure PostgreSQL Row-Level Security policies for tenant isolation
- [X] T043 Create tenant context helper in backend/src/database/tenant_context.py
- [X] T044 Implement tenant scoping in all database queries

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Real-Time Inventory Dashboard (Priority: P1) 🎯 MVP

**Goal**: An Inventory Manager needs to see current stock levels across all warehouses with AI-powered insights and alerts to make informed decisions quickly.

**Independent Test**: Can be fully tested by logging in as an Inventory Manager, navigating to the inventory dashboard, and verifying that real-time stock levels, AI indicators, and alerts are displayed correctly.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T045 [P] [US1] Unit test for Product model in backend/tests/unit/models/test_product.py
- [X] T046 [P] [US1] Unit test for Warehouse model in backend/tests/unit/models/test_warehouse.py
- [X] T047 [P] [US1] Unit test for Inventory model in backend/tests/unit/models/test_inventory.py
- [X] T048 [P] [US1] Integration test for inventory list API in backend/tests/integration/test_inventory_api.py
- [X] T049 [P] [US1] Integration test for warehouse filter in backend/tests/integration/test_inventory_api.py
- [X] T050 [P] [US1] Unit test for InventoryDashboard component in frontend/tests/unit/components/inventory/InventoryDashboard.test.tsx
- [X] T051 [P] [US1] E2E test for dashboard navigation in frontend/tests/e2e/dashboard.spec.ts

### Database Models for User Story 1

- [X] T052 [P] [US1] Create Product model in backend/src/models/product.py
- [X] T053 [P] [US1] Create Warehouse model in backend/src/models/warehouse.py
- [X] T054 [P] [US1] Create Inventory model in backend/src/models/inventory.py
- [X] T055 [US1] Create database migration for products, warehouses, inventory tables in backend/alembic/versions/
- [ ] T056 [US1] Run migration and verify schema in database

### Backend Services for User Story 1

- [X] T057 [P] [US1] Create ProductService in backend/src/services/product_service.py
- [X] T058 [P] [US1] Create WarehouseService in backend/src/services/warehouse_service.py
- [X] T059 [US1] Create InventoryService in backend/src/services/inventory_service.py (depends on T052, T053, T054)
- [X] T060 [US1] Implement inventory query with warehouse filtering in backend/src/services/inventory_service.py
- [X] T061 [US1] Implement low stock alert detection in backend/src/services/inventory_service.py

### Backend API Endpoints for User Story 1

- [X] T062 [US1] Create products list endpoint GET /v1/products in backend/src/api/v1/products.py (depends on T057)
- [X] T063 [US1] Create product detail endpoint GET /v1/products/{id} in backend/src/api/v1/products.py
- [X] T064 [US1] Create warehouses list endpoint GET /v1/warehouses in backend/src/api/v1/warehouses.py (depends on T058)
- [X] T065 [US1] Create warehouse detail endpoint GET /v1/warehouses/{id} in backend/src/api/v1/warehouses.py
- [X] T066 [US1] Create inventory list endpoint GET /v1/inventory in backend/src/api/v1/inventory.py (depends on T059)
- [X] T067 [US1] Add warehouse filter parameter to inventory endpoint in backend/src/api/v1/inventory.py
- [X] T068 [US1] Add low_stock filter parameter to inventory endpoint in backend/src/api/v1/inventory.py

### Real-Time Updates Infrastructure

- [X] T069 [US1] Setup WebSocket connection handler in backend/src/api/websocket.py
- [X] T070 [US1] Implement inventory update broadcast in backend/src/services/inventory_service.py
- [ ] T071 [US1] Create WebSocket client service in frontend/src/services/websocket.ts

### Frontend Components for User Story 1

- [X] T072 [P] [US1] Create Product model/types in frontend/src/types/product.ts
- [X] T073 [P] [US1] Create Warehouse model/types in frontend/src/types/warehouse.ts
- [X] T074 [P] [US1] Create Inventory model/types in frontend/src/types/inventory.ts
- [X] T075 [US1] Create InventoryDashboard page component in frontend/src/pages/Inventory/Dashboard.tsx
- [X] T076 [US1] Create InventoryList component in frontend/src/components/inventory/InventoryList.tsx
- [X] T077 [US1] Create WarehouseFilter component in frontend/src/components/inventory/WarehouseFilter.tsx
- [X] T078 [US1] Create StockLevelIndicator component for visual indicators in frontend/src/components/inventory/StockLevelIndicator.tsx
- [X] T079 [US1] Integrate WebSocket for real-time updates in frontend/src/pages/Inventory/Dashboard.tsx
- [X] T080 [US1] Add inventory API hooks in frontend/src/hooks/useInventory.ts
- [X] T081 [US1] Create dashboard route in frontend/src/App.tsx

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Inventory Manager can view dashboard with real-time stock levels.

---

## Phase 4: User Story 2 - Perform Inventory Movements (Priority: P1)

**Goal**: Warehouse Staff need to record inventory movements (inbound, outbound, transfers) to maintain accurate stock levels across warehouses.

**Independent Test**: Can be fully tested by logging in as Warehouse Staff, performing an inbound movement (receiving stock), and verifying that the inventory levels update correctly and the movement is recorded in the audit trail.

### Tests for User Story 2 ⚠️

- [ ] T082 [P] [US2] Unit test for InventoryMovement model in backend/tests/unit/models/test_inventory_movement.py
- [ ] T083 [P] [US2] Unit test for inventory movement validation in backend/tests/unit/services/test_inventory_service.py
- [ ] T084 [P] [US2] Unit test for optimistic locking in backend/tests/unit/services/test_inventory_service.py
- [ ] T085 [P] [US2] Integration test for inbound movement API in backend/tests/integration/test_movement_api.py
- [ ] T086 [P] [US2] Integration test for outbound movement with insufficient stock in backend/tests/integration/test_movement_api.py
- [ ] T087 [P] [US2] Integration test for transfer movement atomicity in backend/tests/integration/test_movement_api.py
- [ ] T088 [P] [US2] Integration test for concurrent movement handling in backend/tests/integration/test_movement_api.py
- [ ] T089 [P] [US2] Unit test for MovementForm component in frontend/tests/unit/components/inventory/MovementForm.test.tsx
- [ ] T090 [P] [US2] E2E test for inventory movement workflow in frontend/tests/e2e/movements.spec.ts

### Database Models for User Story 2

- [X] T091 [US2] Create InventoryMovement model in backend/src/models/inventory_movement.py
- [X] T092 [US2] Add version column for optimistic locking to Inventory model in backend/src/models/inventory.py
- [X] T093 [US2] Create database migration for inventory_movements table in backend/alembic/versions/
- [X] T094 [US2] Update inventory table migration to add version column in backend/alembic/versions/

### Backend Services for User Story 2

- [X] T095 [US2] Implement inbound movement logic in backend/src/services/inventory_service.py
- [X] T096 [US2] Implement outbound movement logic with stock validation in backend/src/services/inventory_service.py
- [X] T097 [US2] Implement transfer movement with atomic transaction in backend/src/services/inventory_service.py
- [X] T098 [US2] Implement optimistic locking check in backend/src/services/inventory_service.py
- [X] T099 [US2] Implement movement conflict handling and queuing in backend/src/services/inventory_service.py
- [X] T100 [US2] Integrate audit logging for movements in backend/src/services/inventory_service.py
- [X] T101 [US2] Create movement history query service in backend/src/services/inventory_service.py

### Backend API Endpoints for User Story 2

- [X] T102 [US2] Create movement creation endpoint POST /v1/inventory/movement in backend/src/api/v1/inventory.py
- [X] T103 [US2] Create movement history endpoint GET /v1/inventory/movements in backend/src/api/v1/inventory.py
- [X] T104 [US2] Add movement type validation in backend/src/api/v1/inventory.py
- [X] T105 [US2] Add stock validation error handling in backend/src/api/v1/inventory.py

### Frontend Components for User Story 2

- [X] T106 [US2] Create InventoryMovement model/types in frontend/src/types/inventory_movement.ts
- [X] T107 [US2] Create MovementForm component for inbound/outbound/transfer in frontend/src/components/inventory/MovementForm.tsx
- [X] T108 [US2] Create MovementHistory component in frontend/src/components/inventory/MovementHistory.tsx
- [X] T109 [US2] Add movement API hooks in frontend/src/hooks/useMovements.ts
- [X] T110 [US2] Create movements page route in frontend/src/pages/Inventory/Movements.tsx
- [X] T111 [US2] Add navigation link to movements page in frontend/src/components/layout/BaseLayout.tsx
- [X] T112 [US2] Add form validation and error handling in frontend/src/components/inventory/MovementForm.tsx
- [X] T113 [US2] Integrate real-time inventory update after movement in frontend/src/components/inventory/MovementForm.tsx

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Warehouse Staff can record movements and see real-time updates.

---

## Phase 5: User Story 3 - Receive AI Replenishment Recommendations (Priority: P2)

**Goal**: An Inventory Manager needs to receive AI-generated recommendations for when and how much inventory to reorder to prevent stockouts and optimize inventory levels.

**Independent Test**: Can be fully tested by having products with low stock levels, viewing AI recommendations, and verifying that recommendations include reorder quantities, timing, and explanations.

### Tests for User Story 3 ⚠️

- [ ] T114 [P] [US3] Unit test for Forecast model in backend/tests/unit/models/test_forecast.py
- [ ] T115 [P] [US3] Unit test for AIRecommendation model in backend/tests/unit/models/test_ai_recommendation.py
- [ ] T116 [P] [US3] Integration test for forecast API in backend/tests/integration/test_forecast_api.py
- [ ] T117 [P] [US3] Integration test for recommendations API in backend/tests/integration/test_recommendations_api.py
- [ ] T118 [P] [US3] Unit test for forecast service integration in backend/tests/unit/services/test_forecast_service.py
- [ ] T119 [P] [US3] Unit test for AI service client in ai-service/tests/test_api_client.py
- [ ] T120 [P] [US3] Unit test for forecasting model in ai-service/tests/test_forecast_model.py
- [ ] T121 [P] [US3] Unit test for RecommendationsList component in frontend/tests/unit/components/recommendations/RecommendationsList.test.tsx
- [ ] T122 [P] [US3] E2E test for viewing recommendations in frontend/tests/e2e/recommendations.spec.ts

### Database Models for User Story 3

- [X] T123 [US3] Create Forecast model in backend/src/models/forecast.py
- [X] T124 [US3] Create AIRecommendation model in backend/src/models/ai_recommendation.py
- [X] T125 [US3] Create database migration for forecasts table in backend/alembic/versions/
- [X] T126 [US3] Create database migration for ai_recommendations table in backend/alembic/versions/

### AI Service Implementation

- [X] T127 [P] [US3] Setup AI service FastAPI application in ai-service/src/main.py
- [X] T128 [P] [US3] Implement time-series forecasting model in ai-service/src/models/forecasting/forecast_model.py
- [X] T129 [P] [US3] Create forecast generation endpoint POST /forecast in ai-service/src/api/forecast_api.py
- [X] T130 [P] [US3] Implement recommendation calculation service in ai-service/src/services/recommendation_service.py
- [X] T131 [P] [US3] Create recommendation endpoint POST /recommendations in ai-service/src/api/recommendations_api.py
- [X] T132 [P] [US3] Implement model versioning in ai-service/src/registry/model_registry.py
- [X] T133 [P] [US3] Implement explainability module in ai-service/src/services/explainability.py

### Backend Services for User Story 3

- [X] T134 [US3] Create ForecastService with AI service integration in backend/src/services/forecast_service.py
- [X] T135 [US3] Create RecommendationService with AI service integration in backend/src/services/recommendation_service.py
- [X] T136 [US3] Implement recommendation priority ranking in backend/src/services/recommendation_service.py
- [ ] T137 [US3] Implement scheduled forecast generation job in backend/src/services/forecast_service.py
- [X] T138 [US3] Create AI service API client in backend/src/services/ai_service_client.py

### Backend API Endpoints for User Story 3

- [X] T139 [US3] Create forecast list endpoint GET /v1/forecast in backend/src/api/v1/forecasts.py (depends on T134)
- [X] T140 [US3] Create recommendations list endpoint GET /v1/recommendations in backend/src/api/v1/recommendations.py (depends on T135)
- [X] T141 [US3] Create recommendation explanation endpoint GET /v1/recommendations/{id}/explanation in backend/src/api/v1/recommendations.py
- [X] T142 [US3] Add urgency and status filtering to recommendations endpoint in backend/src/api/v1/recommendations.py

### Frontend Components for User Story 3

- [X] T143 [US3] Create Forecast model/types in frontend/src/types/forecast.ts
- [X] T144 [US3] Create Recommendation model/types in frontend/src/types/recommendation.ts
- [X] T145 [US3] Create RecommendationsList component in frontend/src/components/recommendations/RecommendationsList.tsx
- [X] T146 [US3] Create RecommendationDetail component with explanation in frontend/src/components/recommendations/RecommendationDetail.tsx
- [X] T147 [US3] Create ForecastChart component for visualization in frontend/src/components/recommendations/ForecastChart.tsx
- [X] T148 [US3] Create recommendations dashboard page in frontend/src/pages/Recommendations/Dashboard.tsx
- [X] T149 [US3] Add recommendations API hooks in frontend/src/hooks/useRecommendations.ts
- [X] T150 [US3] Add navigation link to recommendations page in frontend/src/components/layout/BaseLayout.tsx

**Checkpoint**: At this point, User Story 3 should be functional. Inventory Managers can view AI-generated recommendations with explanations.

---

## Phase 6: User Story 4 - Approve AI-Generated Purchase Orders (Priority: P2)

**Goal**: An Inventory Manager needs to review and approve purchase orders that were generated from AI recommendations, ensuring they meet business requirements before sending to suppliers.

**Independent Test**: Can be fully tested by having AI-generated purchase order recommendations, reviewing the purchase order details, approving it, and verifying it moves to the approved state.

### Tests for User Story 4 ⚠️

- [ ] T151 [P] [US4] Unit test for Supplier model in backend/tests/unit/models/test_supplier.py
- [ ] T152 [P] [US4] Unit test for PurchaseOrder model in backend/tests/unit/models/test_purchase_order.py
- [ ] T153 [P] [US4] Unit test for PurchaseOrderItem model in backend/tests/unit/models/test_purchase_order_item.py
- [ ] T154 [P] [US4] Integration test for purchase order creation API in backend/tests/integration/test_purchase_order_api.py
- [ ] T155 [P] [US4] Integration test for purchase order approval API in backend/tests/integration/test_purchase_order_api.py
- [ ] T156 [P] [P] [US4] Integration test for purchase order state machine in backend/tests/integration/test_purchase_order_api.py
- [ ] T157 [P] [US4] Unit test for PurchaseOrderList component in frontend/tests/unit/components/purchase-orders/PurchaseOrderList.test.tsx
- [ ] T158 [P] [US4] E2E test for purchase order approval workflow in frontend/tests/e2e/purchase-orders.spec.ts

### Database Models for User Story 4

- [X] T159 [US4] Create Supplier model in backend/src/models/supplier.py
- [X] T160 [US4] Create PurchaseOrder model in backend/src/models/purchase_order.py
- [X] T161 [US4] Create PurchaseOrderItem model in backend/src/models/purchase_order_item.py
- [X] T162 [US4] Create database migration for suppliers table in backend/alembic/versions/
- [X] T163 [US4] Create database migration for purchase_orders table in backend/alembic/versions/
- [X] T164 [US4] Create database migration for purchase_order_items table in backend/alembic/versions/

### Backend Services for User Story 4

- [X] T165 [P] [US4] Create SupplierService in backend/src/services/supplier_service.py
- [X] T166 [US4] Create PurchaseOrderService with state machine in backend/src/services/purchase_order_service.py
- [X] T167 [US4] Implement PO creation from AI recommendation in backend/src/services/purchase_order_service.py
- [X] T168 [US4] Implement PO approval with RBAC check in backend/src/services/purchase_order_service.py
- [X] T169 [US4] Implement PO modification before approval in backend/src/services/purchase_order_service.py
- [X] T170 [US4] Implement PO receipt and inventory update in backend/src/services/purchase_order_service.py
- [X] T171 [US4] Implement supplier performance tracking in backend/src/services/supplier_service.py

### Backend API Endpoints for User Story 4

- [X] T172 [US4] Create suppliers list endpoint GET /v1/suppliers in backend/src/api/v1/suppliers.py (depends on T165)
- [X] T173 [US4] Create supplier detail endpoint GET /v1/suppliers/{id} in backend/src/api/v1/suppliers.py
- [X] T174 [US4] Create purchase orders list endpoint GET /v1/purchase-orders in backend/src/api/v1/purchase_orders.py (depends on T166)
- [X] T175 [US4] Create purchase order detail endpoint GET /v1/purchase-orders/{id} in backend/src/api/v1/purchase_orders.py
- [X] T176 [US4] Create purchase order creation endpoint POST /v1/purchase-orders in backend/src/api/v1/purchase_orders.py
- [X] T177 [US4] Create purchase order update endpoint PUT /v1/purchase-orders/{id} in backend/src/api/v1/purchase_orders.py
- [X] T178 [US4] Create purchase order approval endpoint POST /v1/purchase-orders/{id}/approve in backend/src/api/v1/purchase_orders.py
- [X] T179 [US4] Add RBAC permission check to approval endpoint in backend/src/api/v1/purchase_orders.py

### Frontend Components for User Story 4

- [X] T180 [US4] Create Supplier model/types in frontend/src/types/supplier.ts
- [X] T181 [US4] Create PurchaseOrder model/types in frontend/src/types/purchase_order.ts
- [ ] T182 [US4] Create SupplierList component in frontend/src/components/suppliers/SupplierList.tsx
- [X] T183 [US4] Create PurchaseOrderList component in frontend/src/components/purchase-orders/PurchaseOrderList.tsx
- [X] T184 [US4] Create PurchaseOrderDetail component with tabs in frontend/src/components/purchase-orders/PurchaseOrderDetail.tsx
- [ ] T185 [US4] Create PurchaseOrderForm component in frontend/src/components/purchase-orders/PurchaseOrderForm.tsx
- [X] T186 [US4] Create PO approval workflow UI in frontend/src/components/purchase-orders/ApprovalWorkflow.tsx
- [X] T187 [US4] Create purchase orders page route in frontend/src/pages/PurchaseOrders/List.tsx
- [X] T188 [US4] Add purchase order API hooks in frontend/src/hooks/usePurchaseOrders.ts
- [X] T189 [US4] Add navigation link to purchase orders page in frontend/src/components/layout/BaseLayout.tsx

**Checkpoint**: At this point, User Story 4 should be functional. Inventory Managers can review and approve AI-generated purchase orders.

---

## Phase 7: User Story 5 - Voice Interaction with AI Assistant (Priority: P3)

**Goal**: Warehouse Staff and Inventory Managers need to ask inventory-related questions using voice and receive spoken responses, enabling hands-free operation during warehouse activities.

**Independent Test**: Can be fully tested by activating voice input, asking a question about stock availability, and verifying that the system responds with both spoken audio and displayed text.

### Tests for User Story 5 ⚠️

- [ ] T190 [P] [US5] Unit test for AIInteraction model in backend/tests/unit/models/test_ai_interaction.py
- [ ] T191 [P] [US5] Integration test for voice query API in backend/tests/integration/test_voice_api.py
- [ ] T192 [P] [US5] Unit test for speech-to-text service in voice-service/tests/test_speech_to_text.py
- [ ] T193 [P] [US5] Unit test for text-to-speech service in voice-service/tests/test_text_to_speech.py
- [ ] T194 [P] [US5] Unit test for NLP intent recognition in voice-service/tests/test_nlp_processor.py
- [ ] T195 [P] [US5] Unit test for VoiceInput component in frontend/tests/unit/components/voice/VoiceInput.test.tsx
- [ ] T196 [P] [US5] E2E test for voice query workflow in frontend/tests/e2e/voice.spec.ts

### Database Models for User Story 5

- [X] T197 [US5] Create AIInteraction model in backend/src/models/ai_interaction.py
- [X] T198 [US5] Create database migration for ai_interactions table in backend/alembic/versions/

### Voice Service Implementation

- [X] T199 [P] [US5] Setup voice service FastAPI application in voice-service/src/main.py
- [X] T200 [P] [US5] Implement speech-to-text service with Web Speech API fallback in voice-service/src/speech_to_text/service.py
- [X] T201 [P] [US5] Implement text-to-speech service in voice-service/src/text_to_speech/service.py
- [X] T202 [P] [US5] Implement NLP intent classifier for inventory domain in voice-service/src/nlp_processor/intent_classifier.py
- [X] T203 [P] [US5] Implement query response generation in voice-service/src/nlp_processor/response_generator.py
- [X] T204 [P] [US5] Create voice query endpoint POST /voice/query in voice-service/src/api/voice_api.py
- [X] T205 [P] [US5] Implement noise reduction for warehouse environments in voice-service/src/speech_to_text/noise_reduction.py

### Backend Services for User Story 5

- [X] T206 [US5] Create VoiceService with voice service integration in backend/src/services/voice_service.py
- [X] T207 [US5] Implement voice query processing and routing in backend/src/services/voice_service.py
- [X] T208 [US5] Implement voice query audit logging in backend/src/services/voice_service.py
- [ ] T209 [US5] Implement voice query caching in backend/src/services/voice_service.py
- [X] T210 [US5] Create voice service API client in backend/src/services/voice_service_client.py

### Backend API Endpoints for User Story 5

- [ ] T211 [US5] Create voice query endpoint POST /v1/ai/voice/query in backend/src/api/v1/ai_query.py (depends on T206)
- [ ] T212 [US5] Add intent routing logic in backend/src/api/v1/ai_query.py
- [ ] T213 [US5] Add voice query history endpoint GET /v1/ai/interactions in backend/src/api/v1/ai_query.py

### Frontend Components for User Story 5

- [X] T214 [US5] Create VoiceQuery model/types in frontend/src/types/voice.ts
- [X] T215 [US5] Create VoiceInput component with push-to-talk in frontend/src/components/voice/VoiceInput.tsx
- [X] T216 [US5] Create VoiceResponse component with audio playback in frontend/src/components/voice/VoiceResponse.tsx
- [X] T217 [US5] Implement real-time transcription display in frontend/src/components/voice/VoiceInput.tsx
- [X] T218 [US5] Implement text input fallback on voice failure in frontend/src/components/voice/VoiceInput.tsx
- [X] T219 [US5] Create voice query history view in frontend/src/components/voice/VoiceHistory.tsx
- [X] T220 [US5] Create voice settings component in frontend/src/components/voice/VoiceSettings.tsx
- [X] T221 [US5] Add offline mode indicator in frontend/src/components/voice/VoiceInput.tsx
- [X] T222 [US5] Implement offline query queuing in frontend/src/services/voice.ts
- [X] T223 [US5] Add voice API hooks in frontend/src/hooks/useVoice.ts
- [X] T224 [US5] Add voice assistant to navigation in frontend/src/components/layout/BaseLayout.tsx

**Checkpoint**: At this point, User Story 5 should be functional. Users can ask voice queries and receive spoken responses.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Global Search

- [ ] T225 [P] Implement global search service in backend/src/services/search_service.py
- [ ] T226 [P] Create global search endpoint POST /v1/search in backend/src/api/v1/search.py
- [ ] T227 [P] Create GlobalSearch component in frontend/src/components/common/GlobalSearch.tsx
- [ ] T228 [P] Integrate global search in navigation in frontend/src/components/layout/BaseLayout.tsx

### Advanced Filtering & Analytics

- [ ] T229 [P] Implement advanced filtering for inventory in backend/src/services/inventory_service.py
- [ ] T230 [P] Create analytics dashboard service in backend/src/services/analytics_service.py
- [ ] T231 [P] Create analytics endpoint GET /v1/analytics in backend/src/api/v1/analytics.py
- [ ] T232 [P] Create AnalyticsDashboard component in frontend/src/components/analytics/AnalyticsDashboard.tsx

### Performance Optimization

- [ ] T233 [P] Implement Redis caching for inventory queries in backend/src/services/inventory_service.py
- [ ] T234 [P] Implement database query optimization and indexes in backend/alembic/versions/
- [ ] T235 [P] Implement frontend code splitting by route in frontend/src/App.tsx
- [ ] T236 [P] Implement frontend virtual scrolling for large lists in frontend/src/components/common/DataTable.tsx

### Error Handling & Resilience

- [ ] T237 [P] Implement circuit breaker for AI service calls in backend/src/services/ai_service_client.py
- [ ] T238 [P] Implement graceful degradation when AI service unavailable in backend/src/services/forecast_service.py
- [ ] T239 [P] Implement retry logic for voice service calls in backend/src/services/voice_service_client.py
- [ ] T240 [P] Add comprehensive error boundaries in frontend/src/components/common/ErrorBoundary.tsx

### Documentation

- [ ] T241 [P] Update API documentation with all endpoints in backend/src/main.py
- [ ] T242 [P] Create user documentation in docs/user-guide.md
- [ ] T243 [P] Create developer documentation in docs/developer-guide.md
- [ ] T244 [P] Update quickstart.md with latest changes

### Security Hardening

- [X] T245 [P] Implement rate limiting on API endpoints in backend/src/api/middleware/rate_limit.py
- [X] T246 [P] Implement input validation and sanitization in backend/src/api/middleware/validation.py
- [X] T247 [P] Add security headers middleware in backend/src/api/middleware/security.py
- [ ] T248 [P] Implement PII masking in logs in backend/src/config/logging.py

### Testing & Quality

- [ ] T249 [P] Add load tests for API endpoints in backend/tests/load/
- [ ] T250 [P] Add performance tests for frontend components in frontend/tests/performance/
- [ ] T251 [P] Achieve 80% code coverage across all services
- [ ] T252 [P] Run quickstart.md validation and update if needed

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS all user stories**
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2 → US3 → US4 → US5)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Depends on US1 entities (Product, Warehouse, Inventory) but should be independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 entities (Inventory) but should be independently testable
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Depends on US3 (AIRecommendation) but should be independently testable with mock data
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - Depends on US1/US2/US4 APIs but should be independently testable

### Within Each User Story

- Tests (TDD) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Backend before frontend (where dependencies exist)
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks (Phase 1) marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Backend and frontend tasks within a story marked [P] can run in parallel (after API contracts defined)
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all model tests for User Story 1 together:
Task: T045 [P] [US1] Unit test for Product model in backend/tests/unit/models/test_product.py
Task: T046 [P] [US1] Unit test for Warehouse model in backend/tests/unit/models/test_warehouse.py
Task: T047 [P] [US1] Unit test for Inventory model in backend/tests/unit/models/test_inventory.py

# Launch all model implementations for User Story 1 together:
Task: T052 [P] [US1] Create Product model in backend/src/models/product.py
Task: T053 [P] [US1] Create Warehouse model in backend/src/models/warehouse.py
Task: T054 [P] [US1] Create Inventory model in backend/src/models/inventory.py

# Launch all frontend type definitions together:
Task: T072 [P] [US1] Create Product model/types in frontend/src/types/product.ts
Task: T073 [P] [US1] Create Warehouse model/types in frontend/src/types/warehouse.ts
Task: T074 [P] [US1] Create Inventory model/types in frontend/src/types/inventory.ts
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (View Real-Time Inventory Dashboard)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Dashboard)
   - Developer B: User Story 2 (Movements) - can start after US1 models exist
   - Developer C: AI Service setup for User Story 3
   - Developer D: Voice Service setup for User Story 5
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies within the same phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- TDD: Write tests FIRST, ensure they FAIL before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Constitution requires 80% code coverage - ensure tests are comprehensive
- All database migrations must be reviewed for performance and security

