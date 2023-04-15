class Date():

    """Simplified date object that can formatted string to
    query a specific date in a twitter query."""

    def __init__(self, year: int, month: int, day: int):
        self.year = year
        self.month = month
        self.day = day
        if(not self.validate()): self.date = None

    def validate(self):
        if (self.month < 1) or (self.month > 12) or \
            not(2007 < self.year < 2023) or not(self.day >= 1): 
            return False
        
        daysInMonth = 30 if self.month % 2 == 0 else 31
        if self.month == 2: #February
            daysInMonth = 29 if self.isLeapYear() else 28
        return self.day <= daysInMonth
    
    def isLeapYear(self):
        return (((self.year % 4 == 0) and (self.year % 100 != 0)) 
                or (self.year % 400 == 0))

    def asString(self):
        return "{y}-{m}-{d}".format(y = self.year, m = self.month, 
                                    d = self.day)

    def asQuery(self, extend = 0) -> str:
        since = f"since:{self.year}-{self.month:02d}-{self.day:02d}"
        until = f"until:{self.year}-{self.month:02d}-{(self.day + 1 + extend):02d}"
        return f"{since} {until}"