class UserGroups:
    ADMIN = 'admin'
    DELIVERY_AGENT = 'delivery_agent'
    CUSTOMER = 'customer'

class OrderStatus:
    PENDING = 'pending'
    ASIGNED = 'asigned'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'

class Errormessages:
    INVALID_SERIALIZER = 'Please enter Correct Input'
    NOT_FOUND = 'please enter a valid id'
    FAILED = 'Please Try Again After Sometime'