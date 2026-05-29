## Purpose  
This assessment evaluates your ability to:  
1. Design and build agentic AI systems in a realistic enterprise setting  
2. Integrate key infrastructure components, including authentication, database, cache, and containerisation  
3. Apply sound engineering judgement and produce production-quality code  
4. Use AI coding tools effectively while demonstrating clear understanding of their output  
5. Communicate technical decisions clearly to both technical and non-technical audiences  

---

##  The Brief  

### Client Scenario  
Your fictional client is **Acme Operations**, a mid-sized organisation aiming to improve the efficiency of customer support and account management.  

Internal users across sales, support, and operations need to answer questions such as:  

> “Show open customer issues for Client X, summarise the latest status, and suggest the next action.”  

Currently, this requires navigating multiple systems manually. Your task is to build an agentic assistant that makes this process seamless, secure, and auditable.  

---

### What You Are Building  
You are required to build a minimal working prototype of an agentic enterprise assistant with the following capabilities:  

1. Authenticate users via Keycloak  
2. Accept user queries via a simple UI or API  
3. Use an LLM agent to determine which tools to call  
4. Query structured data from PostgreSQL  
5. Use Redis for short-term memory or session state  
6. Expose at least one MCP (Model Context Protocol) tool or server  
7. Implement at least one reusable skill or workflow  
8. Run locally using Docker Compose  
9. Include basic evaluation and observability  

---

## Technical Requirements  

The following sections describe each required component. Any trade-offs must be documented clearly in your README and explained during the panel session.  

---

###  Agent and Tools  
The assistant must use an LLM agent that dynamically selects tools. Hard-coded or prompt-only solutions are not acceptable.  

At minimum, the agent must support:  
1. Retrieving a customer profile by name  
2. Retrieving all open issues for a customer  
3. Summarising the history of a specific issue  
4. Creating a recommended next action for an issue  

---

###  MCP (Model Context Protocol)  
You must include at least one MCP server. Examples include:  

1. PostgreSQL MCP server  
2. Filesystem MCP server  
3. Custom MCP server with domain-specific tools  
4. Browser or search MCP mock  

Your README and presentation must explain:  
- Why MCP is useful in this context  
- How it separates tool definitions from agent logic  

---

###  Skills  
You must implement at least one reusable skill (a structured and repeatable workflow).  

#### Suggested Skill: Customer Escalation Summary  
- **Input:** Customer name, open issues, recent activity  
- **Output:**  
  1. Executive summary  
  2. Risk level (Low, Medium, High, Critical)  
  3. Recommended next action  
  4. Missing information  

A skill can be implemented as a prompt template, structured workflow, or reusable function, but must be distinct from a one-off prompt call.  

---

###  Authentication (Keycloak)  
Keycloak is a mandatory requirement.  

Your implementation must include:  
1. A working login or token validation flow  
2. Role-based access control with at least:  
   - **sales_user** — read-only access  
   - **support_user** — read and update access  
   - **admin** — full access  

Keycloak must run within Docker Compose. Mocked authentication is not accepted.  

---

###  Containerisation (Docker Compose)  
Your solution must run end-to-end using:  

```
docker compose up
```  

The setup must include:  
1. Application or API service  
2. PostgreSQL  
3. Redis  
4. Keycloak  
5. MCP server (if implemented as a separate service)  

---

###  Database (PostgreSQL)  
Use PostgreSQL as the primary data store.  

The schema must include at least:  
1. customers  
2. issues  
3. issue_updates  
4. next_actions  
5. users or user_roles  

The database must include seeded sample data to demonstrate all capabilities.  

---

###  Memory (Redis)  
Redis must be used for at least one of the following:  
1. Conversation or session memory  
2. User preferences  
3. Cached lookups  
4. Recent tool call results  

Your documentation must explain design choices and trade-offs between Redis and PostgreSQL.  

---

###  Evaluation and Observability  

#### Evaluation  
Include 5 to 10 test questions that measure:  
1. Correct tool selection  
2. Responses grounded in database results  
3. Role-based access control enforcement  
4. Quality of recommended next actions  

#### Observability  
At minimum, include:  
1. Tool call logs  
2. Request and response traces  
3. Error logs  
4. Basic latency tracking  

Additional integrations (for example OpenTelemetry or LangSmith) are a bonus.  

---

###  Use of AI Coding Tools  
You are encouraged to use AI tools such as Copilot or similar.  

You must be able to explain:  
1. What you delegated to AI tools and why  
2. How you reviewed and validated outputs  
3. How you identified and corrected errors  
4. What you would not trust AI tools to handle without human oversight  

---

##  Deliverables  

You must submit the following   

1. **GitHub Repository**  
   - Full source code and configuration files  

2. **README**  
   - Setup instructions  
   - Architecture overview  
   - Trade-offs  
   - AI tool usage  

3. **Architecture Diagram**  
   - System components and data flow  

4. **Evaluation Results**  
   - Test outputs with commentary  

5. **AI Usage Notes**  
   - Summary of how AI tools were used during development  
