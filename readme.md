# Vending Machine API

## Exercise Brief
Design an API for a vending machine, allowing users with a “seller” role to add, update, or remove products, while users with a “buyer” role can deposit coins into the machine and make purchases. The vending machine should only accept 5, 10, 20, 50, and 100 cent coins.

## Tasks
- Framework of choice: FastAPI
- REST API consuming and producing “application/json”
- Implement CRUD for users (POST doesn’t require authentication)
- Implement CRUD for a product model (GET can be called by anyone, while POST, PUT, and DELETE can be called only by the seller user who created the product)
- Implement `/deposit` endpoint so users with a “buyer” role can deposit coins into their vending machine account
- Implement `/buy` endpoint (accepts productId, amount of products) so users with a “buyer” role can buy products with the money they’ve deposited
- Implement `/reset` endpoint so users with a “buyer” role can reset their deposit

## Evaluation Criteria
- [x] Edge cases covered
- [X] Bonus: API tests
- [X] Attention to security
- [x] Dockerized

## Deliverables
- Github repository
- Postman collection or Swagger documentation

## Usage
To run the solution locally:
1. Clone this repository.
2. Ensure Docker is installed on your machine.
3. Navigate to the root directory of the project.
4. Make sure the .env file is setup properly. Two fields required are `DATABASE_URI` and `SECRET_KEY`
5. Run `docker-compose up -d --build` to build and start the Docker containers.
6. Run `docker exec vendor-machine-api pytest` to run the test cases. 
7. Access the Swagger documentation at `http://localhost:port_number/api/docs` to explore and test the API endpoints.
