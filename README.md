# 🚀 Quepter Youth Hub - Project Setup Guide

## 🌍 Project Overview
Quepter Youth Hub is a cutting-edge blockchain-powered ecosystem built on Hedera Hashgraph, designed to empower youth through decentralized finance, AI mentorship, and skill-based rewards. This Django-based platform integrates real-time tokenomics, AI-driven evaluations, and seamless peer-to-peer transactions.

## 🛠️ Technologies Used
- **Backend**: Django
- **Frontend**: HTML, CSS, SCSS, JavaScript & Bootstrap
- **Blockchain**: Hedera Hashgraph (using Hiero SDK)
- **Database**: PostgreSQL (default is SQLite for development)

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip
- virtualenv (recommended)
- PostgreSQL (for production)

### Installation

1. **Clone the repository**
   ```bash
   git clone github.com/techtovio/quepter
   cd quepter
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root with the following variables:
   ```
   SECRET_KEY=your-django-secret-key
   DEBUG=True
   NETWORK=testnet  # or mainnet for production
   OPERATOR_ID=0.0.xxxx
   OPERATOR_KEY=302e...
   Token_ID=0.0.xxxx
   DATABASE_URL=postgres://user:password@localhost:5432/quepter
   ```

5. **Database setup**
   For development (SQLite):
   ```bash
   python manage.py migrate
   ```
   
   For production (PostgreSQL):
   ```bash
   psql -c "CREATE DATABASE quepter;"
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

### Running the Development Server
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## 🔗 Hedera Integration Setup

1. **Hiero SDK Configuration**
   The project uses Hiero SDK for Hedera Hashgraph integration. Ensure your operator credentials are correctly set in the `.env` file.

2. **Testing Token Transfers**
   You can test the QPT token transfers using the provided functions in `wallet/contracts/hedera.py`:
   ```python
   from wallet.contracts.hedera import transfer_tokens, query_balance
   
   # Example usage
   sender_id = "0.0.xxxx"
   sender_key = "302e..."
   recipient_id = "0.0.xxxx"
   amount = 100  # in tinybars
   
   # Transfer tokens
   transfer_tokens(sender_id, sender_key, recipient_id, amount)
   
   # Query balance
   balance = query_balance(recipient_id)
   print(f"Recipient balance: {balance}")
   ```

## 🏗️ Project Structure
```
quepter-youth-hub/
├── accounts/          # User authentication apps
├── clubs/             # Club management functionality
├── proposals/         # Project proposal system
├── wallet/            # Crypto wallet functionality
│   ├── contracts/
│   │   └── hedera.py  # Hedera integration
├── manage.py          # Django management script
└── requirements.txt   # Project dependencies
```

## 🌟 Key Features Implemented
1. **User Authentication System**
2. **Club Management with Treasury Wallets**
3. **Project Proposal System with AI Evaluation**
4. **QPT Token Wallet Integration**
5. **Peer-to-Peer Trading System**
6. **Talent Competition Platform**

## 🚨 Troubleshooting
- **Hedera Connection Issues**: Verify your operator credentials and network settings
- **Transaction Failures**: Ensure sufficient account balance for gas fees
- **Database Errors**: Check your database connection strings in `.env`

## 📜 License
MIT

## 🌎 Join the Quepter Revolution!
Help us build the future of youth empowerment through blockchain and AI technologies!

For any questions or support, please contact kembohititoh@gmail.com.