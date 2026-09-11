import os
from datetime import datetime
# A simple menu of atleast 8 items across 3 categories e.g(MEALS, SNACKS, BEVERAGES) with their prices and availability status (available or not available). 
# The menu should be stored in a dictionary format.
LOG_FILE = "campus_food_log.txt"
orders = []
next_order_id = 1 

MENU={
    "MEALS": {
        "Rice & Beans": {"price": 4000, "available": True},
        "Chips & Chicken": {"price": 7000, "available": True},
        "Matooke & Groundnuts": {"price": 5000, "available": False},
        "Chapati & Beans": {"price": 3000, "available": True}
    },
    "SNACKS": {
        "French Fries": {"price": 2000, "available": True},
        "Chapati(plain)": {"price": 3000, "available": False},
        "Samosa": {"price": 2000, "available": True}
    },
    "BEVERAGES": {
        "Soda(500ml)": {"price": 1000, "available": True},
        "Orange Juice": {"price": 2000, "available": True},
        "Drinking Water": {"price": 1500, "available": False}
    }
}
# Display the menu to the user in a readable format.
def display_menu():
    print("Welcome to the Campus Food Menu!")
    print("----------------------------------")
    for category, items in MENU.items():
        print(f"\n{category}:")
        for item, details in items.items():
            availability = "Available" if details["available"] else "Not Available"
            print(f"  - {item}: UGX {details['price']} ({availability})")
    print("----------------------------------")

# Ordering system that allows users to select items from the menu, specify quantities, and calculate the total cost of their order. 
# The system should also check for item availability and handle cases where an item is not available.
# The system should apply a delivery fee that depends pn the order's total value or distnce band using conditional logic.
# ordering system written by Racheal & Edrina
def place_order():
    order = {}
    order_items = []
    subtotal = 0
    global next_order_id   
    customer_name = input("Enter customer name: ").strip() or "Walk-in Customer"
# The system should ask users to know if it is a dine-in order or a delivery order and apply the appropriate delivery fee if applicable.
    order_type = ""
    while order_type not in ["dine-in", "delivery"]:
        order_type = input("Is this a Dine-in or Delivery order? (Dine-in/Delivery): ").strip().lower()
        if order_type not in ["dine-in", "delivery"]:
            print("Invalid input. Please enter 'Dine-in' or 'Delivery'.")
    while True:
        display_menu()
        category = input("Enter the category you want to order from (or type 'done' to finish): ").strip().upper()
        if category == 'DONE':
            break
        if category not in MENU:
            print("Invalid category. Please try again.")
            continue

        item = input(f"Enter the item you want to order from {category}: ").strip()
        if item not in MENU[category]:
            print("Invalid item. Please try again.")
            continue

        if not MENU[category][item]["available"]:
            print(f"Sorry, {item} is currently not available.")
            continue

        quantity_raw = input(f"Enter the quantity of {item} you want to order: ").strip()
        if not quantity_raw.isdigit() or int(quantity_raw) <= 0:
            print("Invalid quantity. Please enter a positive integer.")
            continue
        quantity = int(quantity_raw)

        item_cost = MENU[category][item]["price"] * quantity
        subtotal += item_cost
        order_items.append({"name": item, "quantity": quantity})
        order[item] = {"quantity": quantity, "cost": item_cost}
        print(f"Added {quantity} x {item} = UGX {item_cost}")

    if not order_items:
        print("No items were ordered.")
        return

    if subtotal > 0:
        if subtotal < 10000:
            delivery_fee = 2000
        elif subtotal < 20000:
            delivery_fee = 1500
        else:
            delivery_fee = 1000

        total = subtotal + delivery_fee
        print("\nOrder Summary:")
        for item, details in order.items():
            print(f"{item}: Quantity: {details['quantity']}, Cost: UGX {details['cost']}")
        print(f"Delivery Fee: UGX {delivery_fee}")
        print(f"Total Cost: UGX {total}")

        new_order = {
            "order_id": next_order_id,
            "customer_name": customer_name,
            "items": order_items,
            "subtotal": subtotal,
            "delivery_fee": delivery_fee,
            "total": total,
            "status": "Pending",
            "rider": None,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        orders.append(new_order)
        save_orders_to_log(new_order)
        print(f"Order #{next_order_id} placed successfully.")
        next_order_id += 1
    else:
        print("No items were ordered.")


def log_order(order, total_cost):
    print("Order logged for record keeping.")

# The system should assign each completed order to an available rider chosen from a list.
# Allows an order's status to be tracked (e.g., pending, in progress, delivered) and updated as the order progresses through the delivery process.
# Prevents the orders from skipping any of the delivery stages and ensures that the order status is updated in the correct sequence.
RIDERS = ["KATO", "MUTYABA", "OKELLO", "NANYONJO", "MERCY"]
rider_busy_status = {rider: False for rider in RIDERS}
STATUS_STAGES = ["Pending", "Out for Delivery", "Delivered"]


def assign_rider():
    for rider, busy in rider_busy_status.items():
        if not busy:
            rider_busy_status[rider] = True
            return rider
    return None


def update_order_status(order_id=None, status=None):
    if not orders:
        print("There are no orders yet.")
        return

    if order_id is None:
        raw_id = input("Enter order number to update: ").strip()
        if not raw_id.isdigit():
            print("Please enter a valid order number.")
            return
        order_id = int(raw_id)

    order = next((entry for entry in orders if entry["order_id"] == order_id), None)
    if order is None:
        print(f"No order found with number {order_id}.")
        return

    current_index = STATUS_STAGES.index(order["status"])
    if current_index == len(STATUS_STAGES) - 1:
        print(f"Order #{order['order_id']} is already 'Delivered'.")
        return

    next_stage = STATUS_STAGES[current_index + 1]

    if next_stage == "Out for Delivery":
        rider = assign_rider()
        if rider is None:
            print("No available riders at the moment. Please wait.")
            return
        order["rider"] = rider
        print(f"Rider {rider} has been assigned to order #{order['order_id']}.")

    if next_stage == "Delivered":
        if order.get("rider"):
            rider_busy_status[order["rider"]] = False
        order["rider"] = order.get("rider")

    order["status"] = next_stage
    order["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_orders_to_log(order)
    print(f"Order #{order['order_id']} status updated to {next_stage}.")


def find_order_by_id(order_id):
    for order in orders:
        if order["order_id"] == order_id:
            return order
    return None


next_status = ["Pending", "Out for Delivery", "Delivered"]


# The rider is assigned at the point of order placement, and the order status is updated as the order progresses through the delivery process.
def simulate_order_delivery_flow(order):
    if order["status"] == "Pending":
        rider = assign_rider()
        if rider is None:
            print("No available riders at the moment. Please wait.")
            return

        order["rider"] = rider
        order["status"] = "Out for Delivery"
        print(f"Rider {rider} has been assigned to order #{order['order_id']}.")
        print(f"Order #{order['order_id']} status updated to {order['status']}.")

    elif order["status"] == "Out for Delivery":
        if order.get("rider"):
            rider_busy_status[order["rider"]] = False
        order["status"] = "Delivered"
        print(f"Rider {order['rider']} is now available for new orders.")
        print(f"Order #{order['order_id']} status updated to {order['status']}.")


# The system should compute and display the day's total revenue, 
# the best-selling item and the number of orders currently in each status category.
def show_report():
    total_revenue = 0
    item_sales = {}
    status_counts = {"Pending": 0, "Out for Delivery": 0, "Delivered": 0}
    if not orders:
        print("\nNo orders have been placed yet.")
        return
 
    total_revenue = sum(order["total"] for order in orders if order["status"] == "Delivered")
 
    # Tally quantities sold per item name, across every order.
    item_totals = {}
    for order in orders:
        for item in order["items"]:
            item_totals[item["name"]] = item_totals.get(item["name"], 0) + item["quantity"]
 
    if item_totals:
        best_seller = max(item_totals, key=item_totals.get)
        best_seller_qty = item_totals[best_seller]
    else:
        best_seller, best_seller_qty = "N/A", 0
 
    status_counts = {status: 0 for status in next_status}
    for order in orders:
        status_counts[order["status"]] += 1
  

    print("------- Daily Report -------")
    print(f"Total Revenue: UGX {total_revenue}")
    print(f"Best Selling Item: {best_seller} (Sold {best_seller_qty} units)" if best_seller != "N/A" else "No items sold today.")
    print("Order Counts:")
    for status, count in status_counts.items():
        print(f"{status}: {count}")

def list_all_orders():
    if not orders:
        print("\nNo orders have been placed yet.")
        return

    print("\n------- All Orders -------")
    for order in orders:
        rider_text = order["rider"] if order["rider"] else "Not yet assigned"
        print(f"#{order['order_id']:<3} {order['customer_name']:<20} "
              f"UGX {order['total']:>8,}  {order['status']:<16} Rider: {rider_text}")
        
# The system should save every order to a log file and reload the log automatically when the program starts
#so that records arent lost between sessions. The log should include the order details, total cost, assigned rider, and timestamps for each stage of the order process.
# Handle errors gracefully, such as invalid menu selections, unavailable items, or issues with file I/O operations.
def load_orders_from_log():
    global next_order_id
 
    if not os.path.exists(LOG_FILE):
        return   # Nothing to load yet - that's fine on first run.
 
    loaded_count = 0
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as log_file:
            for raw_line in log_file:
                raw_line = raw_line.strip()
                if raw_line == "":
                    continue
                parts = raw_line.split("|")
                if len(parts) != 8:
                    continue   # Skip any corrupted/incomplete line rather than crashing.
 
                order_id, customer_name, items_summary, subtotal, delivery_fee, total, rider, timestamp = parts
 
                # Rebuild an approximate items list from the summary so that
                # "best-selling item" reporting still works after a reload.
                rebuilt_items = []
                for chunk in items_summary.split("; "):
                    if " x" in chunk:
                        name, qty = chunk.rsplit(" x", 1)
                        if qty.isdigit():
                            rebuilt_items.append({"name": name, "quantity": int(qty)})
 
                order = {
                    "order_id": int(order_id),
                    "customer_name": customer_name,
                    "items": rebuilt_items,
                    "subtotal": int(subtotal),
                    "delivery_fee": int(delivery_fee),
                    "total": int(total),
                    "status": "Delivered",
                    "rider": None if rider == "N/A" else rider,
                    "timestamp": timestamp,
                }
                orders.append(order)
                loaded_count += 1
                next_order_id = max(next_order_id, order["order_id"] + 1)
    except OSError as error:
        print(f"Warning: could not read the log file ({error}). Starting with an empty order history.")
        return
 
    if loaded_count:
        print(f"Loaded {loaded_count} previously completed order(s) from {LOG_FILE}.")
def save_orders_to_log(order):
    items_summary = "; ".join(
        f"{it['name']} x{it['quantity']}" for it in order["items"]
    )
    line = "|".join([
        str(order["order_id"]),
        order["customer_name"],
        items_summary,
        str(order["subtotal"]),
        str(order["delivery_fee"]),
        str(order["total"]),
        order["rider"] or "N/A",
        order["timestamp"],
    ])
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write(line + "\n")
    except OSError as error:
        print(f"Warning: could not save order #{order['order_id']} to the log file ({error}).") 

# Asimple text-based user interface that allows users to navigate through the different functionalities of the system, such as placing orders, viewing reports, and exiting the program.

def main_menu():
    load_orders_from_log()
    while True:
        print("\n--- Campus Food Ordering System ---")
        print("1. Place an Order")
        print("2. Simulate Order Delivery Flow")
        print("3. Update Order Status")
        print("4. Sales Report")
        print("5. List All Orders")
        print("6. Exit")
        choice = input("Enter your choice: ")
    
        if choice == '1':
            place_order()
        elif choice == '2':
            if not orders:
                print("\nNo orders have been placed yet.")
            else:
                simulate_order_delivery_flow(orders[-1])
        elif choice == '3':
            update_order_status()
        elif choice == '4':
            show_report()
        elif choice == '5':
            list_all_orders()
        elif choice == '6':
            print("THANK YOU FOR USING THE CAMPUS FOOD ORDERING SYSTEM. Goodbye!")
            break


if __name__ == "__main__":
    main_menu()
