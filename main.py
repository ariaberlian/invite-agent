from utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    logger.info("Starting invite-agent application")
    print("Hello from invite-agent!")


if __name__ == "__main__":
    main()
