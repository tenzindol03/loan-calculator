from flask import Flask, render_template, request
from datetime import datetime
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Loan Calculation Logic
def calculate_escrow_payment(total_expenses, down_payment_percentage, annual_interest_rate, months):
    down_payment = total_expenses * down_payment_percentage / 100
    loan_amount = total_expenses - down_payment
    monthly_interest_rate = annual_interest_rate / 12 / 100

    if monthly_interest_rate > 0:
        monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** months) / (
            (1 + monthly_interest_rate) ** months - 1)
    else:
        monthly_payment = loan_amount / months

    return {
        "total_expenses": total_expenses,
        "down_payment": down_payment,
        "loan_amount": loan_amount,
        "monthly_payment": monthly_payment
    }

# Generate Pie Chart for Loan Expenses
def generate_pie_chart(down_payment, loan_amount):
    plt.figure(figsize=(12, 12))  # Larger chart size for better readability
    labels = ['Down Payment', 'Loan Amount']
    sizes = [down_payment, loan_amount]
    colors = ['#F4B443', '#6491DE']
    explode = (0.1, 0)  # Highlight down payment slice

    # Add pie chart details with larger text
    plt.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%',
        startangle=140,
        colors=colors,
        explode=explode,
        textprops={'fontsize': 18, 'color': '#073D7F'}
    )
    plt.title('Loan Expense Breakdown', fontsize=24, color='#073D7F', weight='bold', pad=20)

    # Save chart
    chart_path = os.path.join("static", "loan_pie_chart.png")
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    return chart_path

# Savings Plan Calculation Logic
def calculate_savings_plan(total_expenses, current_savings, monthly_saving_capacity, moving_date):
    today = datetime.now()
    try:
        target_date = datetime.strptime(moving_date, '%Y-%m-%d')
        remaining_months = (target_date.year - today.year) * 12 + (target_date.month - today.month)

        if remaining_months <= 0:
            return {"error": "Invalid moving date. Please select a future date."}

        remaining_amount = total_expenses - current_savings
        required_monthly_saving = remaining_amount / remaining_months

        return {
            "total_expenses": total_expenses,
            "current_savings": current_savings,
            "remaining_amount": remaining_amount,
            "remaining_months": remaining_months,
            "required_monthly_saving": required_monthly_saving
        }
    except Exception as e:
        print(f"Error in savings plan calculation: {e}")
        return {"error": "An error occurred while processing the savings plan."}

# Generate Savings Line Chart
def generate_savings_line_chart(total_expenses, current_savings, monthly_saving_capacity, remaining_months):
    cumulative_savings = [current_savings + monthly_saving_capacity * i for i in range(remaining_months + 1)]
    target_savings = [total_expenses] * (remaining_months + 1)

    plt.figure(figsize=(14, 10))  # Increase chart size
    plt.plot(range(remaining_months + 1), cumulative_savings, label='Cumulative Savings', color='#6491DE', linewidth=3)
    plt.plot(range(remaining_months + 1), target_savings, label='Target Savings', color='#F4B443', linestyle='--', linewidth=3)

    # Add titles and labels with larger fonts
    plt.title('Savings Progress', fontsize=24, color='#073D7F', weight='bold', pad=20)
    plt.xlabel('Months', fontsize=20, color='#073D7F', labelpad=15)
    plt.ylabel('Savings ($)', fontsize=20, color='#073D7F', labelpad=15)

    # Customize legend
    plt.legend(loc='upper left', fontsize=16, frameon=False)

    # Customize ticks
    plt.xticks(fontsize=16, color='#073D7F')
    plt.yticks(fontsize=16, color='#073D7F')

    # Gridlines for readability
    plt.grid(color='gray', linestyle='--', linewidth=0.7, alpha=0.8)

    # Save chart
    chart_path = os.path.join("static", "savings_line_chart.png")
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    return chart_path


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculate', methods=['GET', 'POST'])
def calculate():
    if request.method == 'POST':
        try:
            total_expenses = float(request.form.get('total_expenses', 0))
            down_payment_percentage = float(request.form.get('down_payment_percentage', 0))
            annual_interest_rate = float(request.form.get('annual_interest_rate', 0))
            months = int(request.form.get('months', 0))

            # Validate inputs
            if total_expenses <= 0 or months <= 0:
                raise ValueError("Total expenses and months must be greater than zero.")

            result = calculate_escrow_payment(total_expenses, down_payment_percentage, annual_interest_rate, months)
            pie_chart = generate_pie_chart(result["down_payment"], result["loan_amount"])

            if not pie_chart:
                raise ValueError("Failed to generate pie chart.")

            return render_template('loan_result.html', result=result, pie_chart=pie_chart)
        except Exception as e:
            print(f"Error in calculate: {e}")
            return render_template('error.html', error="An error occurred during the loan calculation.")
    return render_template('calculate.html')

@app.route('/savings_plan', methods=['GET', 'POST'])
def savings_plan():
    if request.method == 'POST':
        try:
            total_expenses = float(request.form.get('total_expenses', 0))
            current_savings = float(request.form.get('current_savings', 0))
            monthly_saving_capacity = float(request.form.get('monthly_saving_capacity', 0))
            moving_date = request.form.get('moving_date', '')

            # Validate inputs
            if total_expenses <= 0 or monthly_saving_capacity <= 0:
                raise ValueError("Total expenses and monthly saving capacity must be greater than zero.")
            if not moving_date:
                raise ValueError("Moving date is required.")

            result = calculate_savings_plan(total_expenses, current_savings, monthly_saving_capacity, moving_date)

            if "error" not in result:
                line_chart = generate_savings_line_chart(total_expenses, current_savings, monthly_saving_capacity, result["remaining_months"])
                if not line_chart:
                    raise ValueError("Failed to generate line chart.")
                return render_template('savings_result.html', result=result, line_chart=line_chart)

            return render_template('savings_result.html', result=result)
        except Exception as e:
            print(f"Error in savings_plan: {e}")
            return render_template('error.html', error="An error occurred in the savings plan calculation.")
    return render_template('savings_plan.html')

if __name__ == '__main__':
    app.run(debug=True)
