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


# ---------------- COMMON CLEAN FUNCTION ----------------
def clean_input(data_dict):
    return {
        k: v for k, v in data_dict.items()
        if k in ["name", "email", "phone", "mobile", "city"]
        and v not in ["", "string", "null", None]
    }


# ---------------- CUSTOMERS ----------------
@app.post("/customers")
def customers(data: RequestModel):
    try:
        raw_data = data.dict(exclude_none=True)

        if data.action == "create":
            if not data.name:
                raise HTTPException(status_code=400, detail="name required")

            clean_data = clean_input(raw_data)
            return odoo_service.create_customer(clean_data)

        elif data.action in ["list", "read"]:
            return odoo_service.get_customers(
                id=data.id,
                name=data.name,
                city=data.city
            )

        elif data.action == "update":
            if not data.id and not data.name:
                raise HTTPException(status_code=400, detail="id or name required")

            clean_data = clean_input(raw_data)

            # ✅ FIX: DO NOT REMOVE NAME (previous bug removed this)
            # clean_data.pop("name", None)  ❌ removed

            # ✅ SAFETY: prevent empty updates
            if not clean_data:
                raise HTTPException(status_code=400, detail="No valid fields to update")

            if data.id:
                return odoo_service.update_partner(data.id, clean_data)
            else:
                records = odoo_service.get_customers(name=data.name)
                if not records:
                    raise HTTPException(status_code=404, detail="record not found")

                return odoo_service.update_partner(records[0]["id"], clean_data)

        elif data.action == "delete":
            if not data.id and not data.name:
                raise HTTPException(status_code=400, detail="id or name required")

            if data.id:
                return odoo_service.delete_partner(data.id)
            else:
                records = odoo_service.get_customers(name=data.name)
                if not records:
                    raise HTTPException(status_code=404, detail="record not found")

                return odoo_service.delete_partner(records[0]["id"])

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
        raw_data = data.dict(exclude_none=True)

        if data.action == "create":
            if not data.name:
                raise HTTPException(status_code=400, detail="name required")

            clean_data = clean_input(raw_data)
            return odoo_service.create_vendor(clean_data)

        elif data.action in ["list", "read"]:
            return odoo_service.get_vendors(
                id=data.id,
                name=data.name,
                city=data.city
            )

        elif data.action == "update":
            if not data.id and not data.name:
                raise HTTPException(status_code=400, detail="id or name required")

            clean_data = clean_input(raw_data)

            # ✅ FIX: DO NOT REMOVE NAME (previous bug removed this)
            # clean_data.pop("name", None)  ❌ removed

            # ✅ SAFETY: prevent empty updates
            if not clean_data:
                raise HTTPException(status_code=400, detail="No valid fields to update")

            if data.id:
                return odoo_service.update_partner(data.id, clean_data)
            else:
                records = odoo_service.get_vendors(name=data.name)
                if not records:
                    raise HTTPException(status_code=404, detail="record not found")

                return odoo_service.update_partner(records[0]["id"], clean_data)

        elif data.action == "delete":
            if not data.id and not data.name:
                raise HTTPException(status_code=400, detail="id or name required")

            if data.id:
                return odoo_service.delete_partner(data.id)
            else:
                records = odoo_service.get_vendors(name=data.name)
                if not records:
                    raise HTTPException(status_code=404, detail="record not found")

                return odoo_service.delete_partner(records[0]["id"])

        else:
            raise HTTPException(status_code=400, detail="Invalid action")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
