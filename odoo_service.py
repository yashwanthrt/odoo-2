import xmlrpc.client
from fastapi import HTTPException


class OdooService:
    def __init__(self):
        self.url = "https://odoo.avowaldatasystems.in".rstrip("/")
        self.db = "odooKmmDb"
        self.username = "rajugenai@gmail.com"
        self.password = "P@$$W0rd&$@"

        self.common = xmlrpc.client.ServerProxy(
            f"{self.url}/xmlrpc/2/common", allow_none=True
        )
        self.models = xmlrpc.client.ServerProxy(
            f"{self.url}/xmlrpc/2/object", allow_none=True
        )

        self.uid = None

        print("OdooService initialized")
        print(f"URL: {self.url}")
        print(f"DB: {self.db}") 
        print(f"Username: {self.username}")
        print(f"Password: {self.password[:4]}****")
    # ---------------- AUTH ----------------
    def authenticate(self):
        if self.uid:
            return self.uid

        uid = self.common.authenticate(
            self.db,
            self.username,
            self.password,
            {}
        )

        if not uid:
            raise HTTPException(status_code=401, detail="Odoo authentication failed")

        self.uid = uid
        return uid

    # ---------------- EXECUTE ----------------
    def execute(self, model, method, args=None, kwargs=None):
        args = args or []
        kwargs = kwargs or {}

        try:
            uid = self.authenticate()
            return self.models.execute_kw(
                self.db, uid, self.password,
                model, method,
                args,
                kwargs
            )
        except Exception:
            # retry once
            self.uid = None
            uid = self.authenticate()
            return self.models.execute_kw(
                self.db, uid, self.password,
                model, method,
                args,
                kwargs
            )

    # ---------------- CREATE ----------------
    def create_partner(self, data, role="customer"):
        partner_data = {
            "name": data.get("name"),
            "email": data.get("email"),
            "phone": data.get("phone"),
            "mobile": data.get("mobile"),
        }

        if role == "customer":
            partner_data["customer_rank"] = 1
        elif role == "vendor":
            partner_data["supplier_rank"] = 1

        partner_data = {k: v for k, v in partner_data.items() if v}

        partner_id = self.execute("res.partner", "create", [partner_data])

        return {"id": partner_id, "message": f"{role} created"}

    def create_customer(self, data):
        return self.create_partner(data, "customer")

    def create_vendor(self, data):
        return self.create_partner(data, "vendor")

    # ---------------- READ ----------------
    def get_partners(self, role="customer", id=None, name=None, city=None):
        domain = []

        if role == "customer":
            domain.append(["customer_rank", ">", 0])
        elif role == "vendor":
            domain.append(["supplier_rank", ">", 0])

        # ✅ FIXED FILTERS
        if id and id != 0:
            domain.append(["id", "=", id])

        if name and name.lower() != "string":
            domain.append(["name", "ilike", name])

        if city and city.lower() != "string":
            domain.append(["city", "ilike", city])

        ids = self.execute("res.partner", "search", [domain])

        if not ids:
            return []

        return self.execute(
            "res.partner",
            "read",
            [ids],
            {"fields": ["id", "name", "email", "phone", "mobile", "city"]}
        )

    def get_customers(self, **filters):
        return self.get_partners("customer", **filters)

    def get_vendors(self, **filters):
        return self.get_partners("vendor", **filters)

    # ---------------- UPDATE ----------------
    def update_partner(self, id, data):
        result = self.execute("res.partner", "write", [[id], data])

        if not result:
            raise HTTPException(status_code=400, detail="Update failed")

        return {"message": "Updated successfully"}

    # ---------------- DELETE ----------------
    def delete_partner(self, id):
        result = self.execute("res.partner", "unlink", [[id]])

        if not result:
            raise HTTPException(status_code=400, detail="Delete failed")

        return {"message": "Deleted successfully"}