# validate date filters v1

        # Request date filters, apply curent month start and end dates if empty

        # Start
        start = request.form.get("filter-start")
        if (start == ""):
            current_date = date.today()
            start = current_date + relativedelta(day=1)
        else:
            # Format date for DB query
            try:
                dt = datetime.fromisoformat(start)
            except:
                dt = datetime.strptime(start, "%Y-%m-%d") 

        # End
        end = request.form.get("filter-end")
        if (end == ""):
            current_date = date.today()
            end = current_date + relativedelta(months=1)
        else:
            # Format date for DB query
            try:
                dt = datetime.fromisoformat(end)
            except:
                dt = datetime.strptime(end, "%Y-%m-%d") 

        # Checks start is before end 
        if (start > end):
            flash("Error: Please end date must be after start date")
            return redirect("/")
        
        # Format date for UI
        month_name = dt.strftime("%B")
        month_year = dt.strftime("%Y")
    
# v2
        # Request start and end dates
        start = request.form.get("filter-start")
        if (start == ""):
            start = None

        end = request.form.get("filter-end")
        if (end == ""):
            end = None

        # Date condition handeling

        # Condition 1: Only inputed start or end dare
        if (start and not end) or (end and not start):
            flash("Error: please select both end and start date")
            return redirect("/")

        match (start, end):
            # Condition 2: User selected no dates
            case (None, None):
                current_date = date.today()
                start = current_date + relativedelta(day=1)
                end = current_date + relativedelta(months=1)
            
            # Condition 3: User selected srat and end dates
            case (s, e):

