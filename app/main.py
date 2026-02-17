from app.core.database import engine

def main():
    with engine.connect() as conn:
        print("Conexão com o banco OK")

if __name__ == "__main__":
    main()
