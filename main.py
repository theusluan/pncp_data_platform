from app.core.config import settings
from app.core.database import engine

def main():
    print("DATABASE_URL carregada:")
    print(settings.DATABASE_URL)   # 👈 TESTE AQUI

    with engine.connect() as conn:
        print("🚀 Banco conectado com sucesso!")

if __name__ == "__main__":
    main()
