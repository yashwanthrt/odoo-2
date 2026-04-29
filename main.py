from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from odoo_service import OdooService

app = FastAPI()
odoo_service = OdooService()


# ---------------- REQUEST MODEL ----------------
class RequestModel(BaseModel):
    action: str
    id: Optional[int] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    city: Optional[str] = None


@app.get("/")
def home():
    return {"message": "API running"}


# ---------------- ✅ COMBINED GET ----------------
@app.get("/partners")
def get_partners(
    role: str = "customer",
    id: Optional[int] = None,
    name: Optional[str] = None,
    city: Optional[str] = None
):
    try:
        print(f" ***************** GET /partners called with id={id}, name={name}, city={city}")

        return odoo_service.get_partners(
            role=role,
            id=id,
            name=name,
            city=city
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- CUSTOMERS ----------------
@app.post("/customers")
def customers(data: RequestModel):
    try:
        if data.action == "create":
            return odoo_service.create_customer(data.dict())

        elif data.action in ["list", "read"]:
            return odoo_service.get_customers(
                id=data.id,
                name=data.name,
                city=data.city
            )

        elif data.action == "update":
            if not data.id:
                raise HTTPException(status_code=400, detail="id required")

            # ✅ FIX APPLIED HERE (ONLY CHANGE)
            allowed_fields = ["name", "email", "phone", "mobile"]

            update_data = {
                k: v for k, v in data.dict(exclude_none=True).items()
                if k in allowed_fields
            }

            return odoo_service.update_partner(data.id, update_data)

        elif data.action == "delete":
            if not data.id:
                raise HTTPException(status_code=400, detail="id required")

            return odoo_service.delete_partner(data.id)

        else:
            raise HTTPException(status_code=400, detail="Invalid action")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- VENDORS ----------------
@app.post("/vendors")
def vendors(data: RequestModel):
    try:
        if data.action == "create":
            return odoo_service.create_vendor(data.dict())

        elif data.action in ["list", "read"]:
            return odoo_service.get_vendors(
                id=data.id,
                name=data.name,
                city=data.city
            )

        elif data.action == "update":
            if not data.id:
                raise HTTPException(status_code=400, detail="id required")

            # ✅ FIX APPLIED HERE (ONLY CHANGE)
            allowed_fields = ["name", "email", "phone", "mobile"]

            update_data = {
                k: v for k, v in data.dict(exclude_none=True).items()
                if k in allowed_fields
            }

            return odoo_service.update_partner(data.id, update_data)

        elif data.action == "delete":
            if not data.id:
                raise HTTPException(status_code=400, detail="id required")

            return odoo_service.delete_partner(data.id)

        else:
            raise HTTPException(status_code=400, detail="Invalid action")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
