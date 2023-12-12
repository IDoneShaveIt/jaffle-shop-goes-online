from datetime import datetime, timedelta
import os
import random
from collections import defaultdict
import hashlib
from utils.csv import (
    split_csv_to_headers_and_data,
    write_to_csv,
)


CURRENT_DIRECTORY_PATH = os.path.dirname(os.path.realpath(__file__))
ORIGINAL_JAFFLE_DATA_DIRECTORY_NAME = "original_jaffle_shop_data"
NEW_JAFFLE_TRAINING_DATA_DIRECORTY_RELATIVE_PATH = (
    "../jaffle_shop_online/seeds/training"
)
NEW_JAFFLE_VALIDATION_DATA_DIRECORTY_RELATIVE_PATH = (
    "../jaffle_shop_online/seeds/validation"
)

CUSTOMERS_COUNT = 2000
ORDERS_COUNT = 10000
TIME_SPAN_IN_DAYS = 30
LOWEST_PAYMENT_IN_HUNDRENDS = 0
HIGHEST_PAYMENT_IN_HUNDRENDS = 28
MAX_PAYMENTS_PER_ORDER = 2


def generate_validation_data():
    generate_customers_data()
    generate_orders_data()
    generate_payments_data()
    generate_signups_data()


def generate_customers_data():
    training_customers_path = os.path.join(
        CURRENT_DIRECTORY_PATH,
        NEW_JAFFLE_TRAINING_DATA_DIRECORTY_RELATIVE_PATH,
        "raw_customers_training.csv",
    )
    validation_customers_path = os.path.join(
        CURRENT_DIRECTORY_PATH,
        NEW_JAFFLE_VALIDATION_DATA_DIRECORTY_RELATIVE_PATH,
        "raw_customers_validation.csv",
    )
    headers, training_customers = split_csv_to_headers_and_data(
        csv_path=training_customers_path
    )
    all_first_names = list(set([row[1] for row in training_customers]))
    all_last_names = list(set([row[2] for row in training_customers]))
    new_customers = [*training_customers]
    for customer_id in range(
        len(training_customers) + 1, len(training_customers) + 201
    ):
        new_customers.append(
            [
                customer_id,  # CUSTOMER ID
                all_first_names[random.randint(0, len(all_first_names) - 1)]
                if random.randint(0, 1)
                else "  ",  # FIRST NAME
                all_last_names[random.randint(0, len(all_last_names) - 1)]
                if random.randint(0, 1)
                else all_first_names[
                    random.randint(0, len(all_first_names) - 1)
                ],  # LAST NAME
            ]
        )
    write_to_csv(validation_customers_path, headers, new_customers)


def generate_orders_data():
    training_orders_path = os.path.join(
        CURRENT_DIRECTORY_PATH,
        NEW_JAFFLE_TRAINING_DATA_DIRECORTY_RELATIVE_PATH,
        "raw_orders_training.csv",
    )
    validation_orders_path = os.path.join(
        CURRENT_DIRECTORY_PATH,
        NEW_JAFFLE_VALIDATION_DATA_DIRECORTY_RELATIVE_PATH,
        "raw_orders_validation.csv",
    )
    validation_customers_path = os.path.join(
        CURRENT_DIRECTORY_PATH,
        NEW_JAFFLE_VALIDATION_DATA_DIRECORTY_RELATIVE_PATH,
        "raw_customers_validation.csv",
    )
    customers_headers, validation_customers = split_csv_to_headers_and_data(
        csv_path=validation_customers_path
    )
    orders_headers, training_orders = split_csv_to_headers_and_data(
        csv_path=training_orders_path
    )
    all_order_statuses = list(set([row[3] for row in training_orders]))
    new_orders = [*training_orders]
    last_order_date = max(
        [datetime.strptime(row[2], "%Y-%m-%d") for row in training_orders]
    )
    validation_orders_date = (last_order_date + timedelta(1)).strftime("%Y-%m-%d")
    for order_id in range(len(training_orders) + 1, len(training_orders) + 51):
        new_orders.append(
            [
                order_id,  # ORDER ID
                random.randint(1, len(validation_customers)),  # CUSTOMER ID
                validation_orders_date,  # ORDER DATE
                all_order_statuses[random.randint(0, len(all_order_statuses) - 1)]
                if random.randint(0, 1)
                else "lost",  # ORDER STATUS
            ]
        )
    write_to_csv(validation_orders_path, orders_headers, new_orders)


def generate_payments_data():
    training_payments_path = os.path.join(
        CURRENT_DIRECTORY_PATH,
        NEW_JAFFLE_TRAINING_DATA_DIRECORTY_RELATIVE_PATH,
        "raw_payments_training.csv",
    )
    validation_payments_path = os.path.join(
        CURRENT_DIRECTORY_PATH,
        NEW_JAFFLE_VALIDATION_DATA_DIRECORTY_RELATIVE_PATH,
        "raw_payments_validation.csv",
    )
    payments_headers, training_payments = split_csv_to_headers_and_data(
        csv_path=training_payments_path
    )
    all_payments_methods = list(set([row[2] for row in training_payments]))
    new_payments = [*training_payments]
    payment_id = len(training_payments) + 1
    for order_id in range(ORDERS_COUNT + 1, ORDERS_COUNT + 51):
        new_payments.append(
            [
                payment_id,  # PAYMENT_ID
                order_id,  # ORDER ID
                all_payments_methods[
                    random.randint(0, len(all_payments_methods) - 1)
                ],  # PAYMENT METHOD
                0,  # AMOUNT
            ]
        )
        payment_id += 1
    write_to_csv(validation_payments_path, payments_headers, new_payments)


def generate_signups_data():
    training_signups_path = os.path.join(
        CURRENT_DIRECTORY_PATH,
        NEW_JAFFLE_TRAINING_DATA_DIRECORTY_RELATIVE_PATH,
        "raw_signups_training.csv",
    )
    validation_signups_path = os.path.join(
        CURRENT_DIRECTORY_PATH,
        NEW_JAFFLE_VALIDATION_DATA_DIRECORTY_RELATIVE_PATH,
        "raw_signups_validation.csv",
    )
    customers_csv_path = os.path.join(
        CURRENT_DIRECTORY_PATH,
        NEW_JAFFLE_VALIDATION_DATA_DIRECORTY_RELATIVE_PATH,
        "raw_customers_validation.csv",
    )
    orders_csv_path = os.path.join(
        CURRENT_DIRECTORY_PATH,
        NEW_JAFFLE_VALIDATION_DATA_DIRECORTY_RELATIVE_PATH,
        "raw_orders_validation.csv",
    )
    customers_headers, customers_data = split_csv_to_headers_and_data(
        csv_path=customers_csv_path
    )
    orders_headers, orders_data = split_csv_to_headers_and_data(
        csv_path=orders_csv_path
    )
    signups_headers, training_signups_data = split_csv_to_headers_and_data(
        csv_path=training_signups_path
    )

    customer_min_order_time_map = defaultdict(
        lambda: (
            datetime.now() - timedelta(random.randint(1, TIME_SPAN_IN_DAYS))
        ).strftime("%Y-%m-%d")
    )
    for order in orders_data:
        customer_min_order_time_map[order[1]] = min(
            datetime.strptime(customer_min_order_time_map[order[1]], "%Y-%m-%d"),
            datetime.strptime(order[2], "%Y-%m-%d"),
        ).strftime("%Y-%m-%d")

    new_signups = [*training_signups_data]
    for customer in customers_data[CUSTOMERS_COUNT + 2 :]:
        new_signups.append(
            [
                customer[0],  # SIGNUP ID
                customer[0],  # CUSTOMER ID
                f"abcd@example.com",  # USER EMAIL
                hashlib.sha256(datetime.now().isoformat().encode()).hexdigest(),
                customer_min_order_time_map[customer[0]],
            ]
        )
    last_signup_date = max(
        [datetime.strptime(row[4], "%Y-%m-%d") for row in training_signups_data]
    )
    validation_signup_date = (last_signup_date + timedelta(1)).strftime("%Y-%m-%d")
    for i in range(len(customers_data) + 1, len(customers_data) + 3):
        new_signups.append(
            [
                i,  # SIGNUP ID
                i,  # CUSTOMER ID
                f"abcd@example.com",  # USER EMAIL
                hashlib.sha256(datetime.now().isoformat().encode()).hexdigest(),
                validation_signup_date,
            ]
        )
    write_to_csv(validation_signups_path, signups_headers, new_signups)


if __name__ == "__main__":
    generate_validation_data()
