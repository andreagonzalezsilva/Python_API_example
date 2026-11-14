import json
import re
import urllib.request

# 1. Lee la clave directamente desde el archivo de configuración de Continue
config_path = "/home/codespace/.continue/config.yaml"

try:
  with open(config_path, "r", encoding="utf-8") as f:
    content = f.read()

  # Busca el patrón de la clave sk-or-v1-...
  match = re.search(r"(sk-or-v1-[a-zA-Z0-9]+)", content)
  if not match:
    print(
        "❌ No se encontró una clave válida de OpenRouter en"
        " ~/.continue/config.yaml"
    )
    exit(1)

  api_key = match.group(1)

  # 2. Consulta el estado de la clave en OpenRouter
  req = urllib.request.Request(
      "https://openrouter.ai/api/v1/key",
      headers={"Authorization": f"Bearer {api_key}"},
  )

  with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())["data"]

  # 3. Muestra el resumen pedagógico
  label = data.get("label", "Estudiante")
  limit = data.get("limit")
  usage = data.get("usage", 0.0)
  limit_remaining = data.get("limit_remaining")

  print("\n" + "=" * 40)
  print(f"📊 ESTADO DE TU SALDO IA ({label})")
  print("=" * 40)
  print(f"• Consumo acumulado : ${usage:.3f} USD")

  if limit is not None:
    print(f"• Límite semanal    : ${limit:.2f} USD")
    print(f"• Saldo restante    : ${limit_remaining:.3f} USD")
  else:
    print("• Límite semanal    : Sin límite asignado")

  print("=" * 40 + "\n")

except Exception as e:
  print(f"Error al verificar el saldo: {e}")