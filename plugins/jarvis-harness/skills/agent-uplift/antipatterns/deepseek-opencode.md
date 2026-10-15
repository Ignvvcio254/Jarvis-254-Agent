# Anti-patrones · deepseek-v4-flash-free (OpenCode)

- [2026-06-10] · Latencia extrema en tier free (>15 min en un caso de benchmark que gemma resuelve en ~2 min) · cola/throttling del tier gratuito · **CONTRAMEDIDA DE ROUTER:** no asignarle tareas en ruta crítica ni interactivas; solo lotes nocturnos o trabajo sin deadline. Confirmar con score del benchmark F0 antes de descartarlo (puede ser lento pero correcto).
