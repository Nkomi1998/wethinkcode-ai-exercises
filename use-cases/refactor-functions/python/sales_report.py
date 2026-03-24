from datetime import datetime


def generate_sales_report(sales_data, report_type='summary', date_range=None,
                         filters=None, grouping=None, include_charts=False,
                         output_format='pdf'):
    """
    Generate a comprehensive sales report based on provided data and parameters.

    Parameters:
    - sales_data: List of sales transactions
    - report_type: 'summary', 'detailed', or 'forecast'
    - date_range: Dict with 'start' and 'end' dates
    - filters: Dict of filters to apply
    - grouping: How to group data ('product', 'category', 'customer', 'region')
    - include_charts: Whether to include charts/visualizations
    - output_format: 'pdf', 'excel', 'html', or 'json'

    Returns:
    - Report data or file path depending on output_format
    """
    # Validate input parameters
    validate_inputs(sales_data, report_type, output_format, date_range)

    # Process and filter data
    filtered_data = process_and_filter_data(sales_data, date_range, filters)

    # Check if we have data after filtering
    if not filtered_data:
        return handle_empty_data(output_format, report_type)

    # Calculate basic metrics
    basic_metrics = calculate_basic_metrics(filtered_data)

    # Group data if specified
    grouped_data = group_data(filtered_data, grouping) if grouping else None

    # Generate report data based on type
    report_data = generate_report_data(
        report_type, filtered_data, basic_metrics, grouped_data,
        date_range, filters, grouping
    )

    # Generate charts if requested
    if include_charts:
        report_data['charts'] = generate_charts_data(filtered_data, grouped_data, grouping)

    # Generate output in the requested format
    return format_output(report_data, output_format, include_charts)


def validate_inputs(sales_data, report_type, output_format, date_range):
    """Validate input parameters."""
    if not sales_data or not isinstance(sales_data, list):
        raise ValueError("Sales data must be a non-empty list")

    if report_type not in ['summary', 'detailed', 'forecast']:
        raise ValueError("Report type must be 'summary', 'detailed', or 'forecast'")

    if output_format not in ['pdf', 'excel', 'html', 'json']:
        raise ValueError("Output format must be 'pdf', 'excel', 'html', or 'json'")

    if date_range:
        if 'start' not in date_range or 'end' not in date_range:
            raise ValueError("Date range must include 'start' and 'end' dates")

        start_date = datetime.strptime(date_range['start'], '%Y-%m-%d')
        end_date = datetime.strptime(date_range['end'], '%Y-%m-%d')

        if start_date > end_date:
            raise ValueError("Start date cannot be after end date")


def process_and_filter_data(sales_data, date_range, filters):
    """Process date range filtering and apply additional filters."""
    filtered_data = sales_data

    # Filter by date range
    if date_range:
        filtered_data = filter_by_date_range(filtered_data, date_range['start'], date_range['end'])

    # Apply additional filters
    if filters:
        filtered_data = apply_additional_filters(filtered_data, filters)

    return filtered_data


def filter_by_date_range(sales_data, start_date_str, end_date_str):
    """Filter sales data by date range."""
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    filtered_data = []
    for sale in sales_data:
        sale_date = datetime.strptime(sale['date'], '%Y-%m-%d')
        if start_date <= sale_date <= end_date:
            filtered_data.append(sale)

    return filtered_data


def apply_additional_filters(sales_data, filters):
    """Apply additional filters to sales data."""
    filtered_data = sales_data
    for key, value in filters.items():
        if isinstance(value, list):
            filtered_data = [sale for sale in filtered_data if sale.get(key) in value]
        else:
            filtered_data = [sale for sale in filtered_data if sale.get(key) == value]
    return filtered_data


def handle_empty_data(output_format, report_type):
    """Handle case when no data matches filters."""
    print("Warning: No data matches the specified criteria")
    if output_format == 'json':
        return {"message": "No data matches the specified criteria", "data": []}
    else:
        # For other formats, generate a minimal report file
        return _generate_empty_report(report_type, output_format)


def calculate_basic_metrics(sales_data):
    """Calculate basic sales metrics."""
    if not sales_data:
        return {}

    total_sales = sum(sale['amount'] for sale in sales_data)
    avg_sale = total_sales / len(sales_data)
    max_sale = max(sales_data, key=lambda x: x['amount'])
    min_sale = min(sales_data, key=lambda x: x['amount'])

    return {
        'total_sales': total_sales,
        'transaction_count': len(sales_data),
        'average_sale': avg_sale,
        'max_sale': max_sale,
        'min_sale': min_sale
    }


def group_data(sales_data, grouping):
    """Group sales data by specified field."""
    grouped_data = {}
    for sale in sales_data:
        key = sale.get(grouping, 'Unknown')
        if key not in grouped_data:
            grouped_data[key] = {
                'count': 0,
                'total': 0,
                'items': []
            }

        grouped_data[key]['count'] += 1
        grouped_data[key]['total'] += sale['amount']
        grouped_data[key]['items'].append(sale)

    # Calculate averages for each group
    for key in grouped_data:
        grouped_data[key]['average'] = grouped_data[key]['total'] / grouped_data[key]['count']

    return grouped_data


def generate_report_data(report_type, sales_data, basic_metrics, grouped_data,
                        date_range, filters, grouping):
    """Generate the main report data structure."""
    report_data = {
        'report_type': report_type,
        'date_generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'date_range': date_range,
        'filters': filters,
        'summary': {
            'total_sales': basic_metrics['total_sales'],
            'transaction_count': basic_metrics['transaction_count'],
            'average_sale': basic_metrics['average_sale'],
            'max_sale': {
                'amount': basic_metrics['max_sale']['amount'],
                'date': basic_metrics['max_sale']['date'],
                'details': basic_metrics['max_sale']
            },
            'min_sale': {
                'amount': basic_metrics['min_sale']['amount'],
                'date': basic_metrics['min_sale']['date'],
                'details': basic_metrics['min_sale']
            }
        }
    }

    # Add grouping data if applicable
    if grouped_data:
        report_data['grouping'] = {
            'by': grouping,
            'groups': {}
        }

        for key, data in grouped_data.items():
            report_data['grouping']['groups'][key] = {
                'count': data['count'],
                'total': data['total'],
                'average': data['average'],
                'percentage': (data['total'] / basic_metrics['total_sales']) * 100
            }

    # Add type-specific data
    if report_type == 'detailed':
        report_data.update(generate_detailed_report_data(sales_data))
    elif report_type == 'forecast':
        report_data.update(generate_forecast_report_data(sales_data))

    return report_data


def generate_detailed_report_data(sales_data):
    """Generate detailed report data with transaction details."""
    transactions = []
    for sale in sales_data:
        transaction = {k: v for k, v in sale.items()}

        # Add calculated fields
        if 'tax' in sale and 'amount' in sale:
            transaction['pre_tax'] = sale['amount'] - sale['tax']

        if 'cost' in sale and 'amount' in sale:
            transaction['profit'] = sale['amount'] - sale['cost']
            transaction['margin'] = (transaction['profit'] / sale['amount']) * 100

        transactions.append(transaction)

    return {'transactions': transactions}


def generate_forecast_report_data(sales_data):
    """Generate forecast report data with trends and projections."""
    # Group sales by month
    monthly_sales = {}
    for sale in sales_data:
        sale_date = datetime.strptime(sale['date'], '%Y-%m-%d')
        month_key = f"{sale_date.year}-{sale_date.month:02d}"

        if month_key not in monthly_sales:
            monthly_sales[month_key] = 0

        monthly_sales[month_key] += sale['amount']

    # Sort months and calculate growth rates
    sorted_months = sorted(monthly_sales.keys())
    growth_rates = []

    for i in range(1, len(sorted_months)):
        prev_month = sorted_months[i-1]
        curr_month = sorted_months[i]

        prev_amount = monthly_sales[prev_month]
        curr_amount = monthly_sales[curr_month]

        if prev_amount > 0:
            growth_rate = ((curr_amount - prev_amount) / prev_amount) * 100
            growth_rates.append(growth_rate)

    # Calculate average growth rate
    avg_growth_rate = sum(growth_rates) / len(growth_rates) if growth_rates else 0

    # Generate forecast for next 3 months
    forecast = {}
    if sorted_months:
        last_month = sorted_months[-1]
        last_amount = monthly_sales[last_month]

        year, month = map(int, last_month.split('-'))

        for i in range(1, 4):
            month += 1
            if month > 12:
                month = 1
                year += 1

            forecast_month = f"{year}-{month:02d}"
            forecast_amount = last_amount * (1 + (avg_growth_rate / 100))
            forecast[forecast_month] = forecast_amount
            last_amount = forecast_amount

    return {
        'forecast': {
            'monthly_sales': monthly_sales,
            'growth_rates': {sorted_months[i]: growth_rates[i-1] for i in range(1, len(sorted_months))},
            'average_growth_rate': avg_growth_rate,
            'projected_sales': forecast
        }
    }


def generate_charts_data(sales_data, grouped_data, grouping):
    """Generate charts data for visualizations."""
    charts_data = {}

    # Sales over time chart
    time_chart = {'labels': [], 'data': []}
    date_sales = {}

    for sale in sales_data:
        if sale['date'] not in date_sales:
            date_sales[sale['date']] = 0
        date_sales[sale['date']] += sale['amount']

    for date in sorted(date_sales.keys()):
        time_chart['labels'].append(date)
        time_chart['data'].append(date_sales[date])

    charts_data['sales_over_time'] = time_chart

    # Add pie chart for grouping if applicable
    if grouped_data:
        pie_chart = {'labels': [], 'data': []}

        for key, data in grouped_data.items():
            pie_chart['labels'].append(key)
            pie_chart['data'].append(data['total'])

        charts_data['sales_by_' + grouping] = pie_chart

    return charts_data


def format_output(report_data, output_format, include_charts):
    """Format the report output based on requested format."""
    if output_format == 'json':
        return report_data
    elif output_format == 'html':
        return _generate_html_report(report_data, include_charts)
    elif output_format == 'excel':
        return _generate_excel_report(report_data, include_charts)
    elif output_format == 'pdf':
        return _generate_pdf_report(report_data, include_charts)


# Helper functions (not implemented here)
def _generate_empty_report(report_type, output_format):
    # Generate an empty report file
    pass

def _generate_html_report(report_data, include_charts):
    # Generate HTML report
    pass

def _generate_excel_report(report_data, include_charts):
    # Generate Excel report
    pass

def _generate_pdf_report(report_data, include_charts):
    # Generate PDF report
    pass