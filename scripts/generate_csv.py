import pandas as pd
import os

data = [
    {"producto": "Arroz Diana 500g", "categoria": "Granos", "precio_cop": 2800, "stock": 340, "pasillo": "3"},
    {"producto": "Aceite Girasol Premier 1L", "categoria": "Aceites", "precio_cop": 9500, "stock": 210, "pasillo": "3"},
    {"producto": "Leche Alqueria Entera 1L", "categoria": "Lacteos", "precio_cop": 4200, "stock": 180, "pasillo": "1"},
    {"producto": "Huevos AA x30", "categoria": "Lacteos", "precio_cop": 15900, "stock": 95, "pasillo": "1"},
    {"producto": "Pollo Entero Fresco kg", "categoria": "Carnes", "precio_cop": 12500, "stock": 60, "pasillo": "2"},
    {"producto": "Papa Pastusa kg", "categoria": "Frutas y Verduras", "precio_cop": 2200, "stock": 400, "pasillo": "4"},
    {"producto": "Banano kg", "categoria": "Frutas y Verduras", "precio_cop": 2600, "stock": 350, "pasillo": "4"},
    {"producto": "Detergente Fab 3kg", "categoria": "Aseo Hogar", "precio_cop": 22900, "stock": 130, "pasillo": "6"},
    {"producto": "Jabon Rey Barra x3", "categoria": "Aseo Hogar", "precio_cop": 8900, "stock": 200, "pasillo": "6"},
    {"producto": "Gaseosa Postobon 1.5L", "categoria": "Bebidas", "precio_cop": 5200, "stock": 260, "pasillo": "5"},
    {"producto": "Cerveza Aguila Lata x6", "categoria": "Bebidas", "precio_cop": 18500, "stock": 150, "pasillo": "5"},
    {"producto": "Cafe Sello Rojo 500g", "categoria": "Granos", "precio_cop": 11200, "stock": 175, "pasillo": "3"},
    {"producto": "Pasta La Muñeca 500g", "categoria": "Granos", "precio_cop": 3100, "stock": 300, "pasillo": "3"},
    {"producto": "Papel Higienico Familia x12", "categoria": "Aseo Hogar", "precio_cop": 19900, "stock": 110, "pasillo": "6"},
    {"producto": "Queso Campesino 500g", "categoria": "Lacteos", "precio_cop": 13500, "stock": 85, "pasillo": "1"},
]

df = pd.DataFrame(data)
out = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "inventario_mercado_central.csv")
df.to_csv(out, index=False, encoding="utf-8")
print(f"OK -> {out}")
print(df)
