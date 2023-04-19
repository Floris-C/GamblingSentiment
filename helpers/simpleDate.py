class Date():

    """Simplified date object that can formatted string to
    query a specific date in a twitter query."""

    def __init__(self, year: int, month: int, day: int): # extend with safe = true/false to switch between None and error?
        self.year = year
        self.month = month
        self.day = day
        if(not self.validate()): self.date = None

    def test(hi="Hello world"):
        print(hi)


    def validate(self):
        if (self.month < 1) or (self.month > 12) or \
            not(2007 < self.year < 2023) or not(self.day >= 1): 
            return False
        
        daysInMonth = 30 if self.month % 2 == 0 else 31
        if self.month == 2: #February
            daysInMonth = 29 if self.isLeapYear() else 28
        return self.day <= daysInMonth
    
    def isLeapYear(self, year = None) -> bool:
        if year == None: year = self.year
        return (((year % 4 == 0) and (year % 100 != 0)) 
                or (year % 400 == 0))

    def asString(self):
        return "{y}-{m:02d}-{d:02d}".format(y = self.year, m = self.month, 
                                    d = self.day)

    def asQuery(self, extend = 0) -> str:
        untilDate = self.day + 1# FML
        print(untilDate)
        
        since = f"since:{self.year}-{self.month:02d}-{self.day:02d}"
        until = f"until:{self.year}-{self.month:02d}-{untilDate:02d}"
        print(self)
        return f"{since} {until}"
    
    def getDaysInMonth(self, month: int, year: int) -> int:
        daysInMonth = 30 if self.month % 2 == 0 else 31
        if self.month == 2: #February
            daysInMonth = 29 if self.isLeapYear() else 28
        return daysInMonth

    
    # def __eq__(self, other): 
    #     if not isinstance(other, MyClass):
    #         # don't attempt to compare against unrelated types
    #         return NotImplemented

    #     return self.foo == other.foo and self.bar == other.bar