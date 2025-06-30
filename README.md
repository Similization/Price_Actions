# Inventory Management System

A FastAPI-based backend for an inventory management system with user authentication, product stock management, and reservation functionality.

## Prerequisites
- Python 3.8+
- PostgreSQL (v12 or higher)

## Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd inventory-management
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up configuration:
   Create a `config.yaml` file in the root directory with the following:
   ```yaml
   db_user: your_db_user
   db_host: localhost
   db_name: inventory
   db_password: your_db_password
   db_port: 5432
   jwt_secret: your_jwt_secret
   port: 8000
   ```

4. Set up the database:
   - Create a PostgreSQL database named `inventory`.
   - Run the SQL schema:
   ```bash
   psql -U your_db_user -d inventory -f src/sql/schema.sql
   ```

5. Start the server:
   ```bash
   python src/main.py
   ```

## API Endpoints
- **Auth**
  - `POST /api/auth/register` - Register a new user
  - `POST /api/auth/login` - Login and get JWT token
- **Products**
  - `GET /api/products` - Get all products
  - `PUT /api/products/{id}/quantity` - Update product quantity (admin only)
- **Reservations**
  - `POST /api/reservations` - Create a reservation
  - `PUT /api/reservations/{id}` - Update a reservation
  - `DELETE /api/reservations/{id}` - Delete a reservation
  - `GET /api/reservations` - Get user's reservations

## Notes
- Passwords in the `users` table are hashed using bcrypt.
- Replace the example hashed passwords in `schema.sql` with actual hashed passwords generated using `passlib`.
- The frontend is not included in this project but can be built separately to interact with this API.