from rest_framework.exceptions import APIException


class CannotUpdateProfile(APIException):
    status_code = 403
    default_detail = (
        "Missing credentials: You cannot update "
        "this profile"
    )
    default_code = "cannot_update_profile"


class CannotCreateNote(APIException):
    status_code = 403
    default_detail = (
        "Missing credentials: Notes can be created "
        "only by Management members or event's support contact"
    )
    default_code = "cannot_create_note"


class CannotCreateClient(APIException):
    status_code = 403
    default_detail = (
        "Missing credentials: Clients can be created "
        "only by Management or Sales members"
    )
    default_code = "cannot_create_client"


class NotInChargeOfClient(APIException):
    status_code = 403
    default_detail = "You are not in charge of this client"
    default_code = "not_in_charge_of_client"


class NotInChargeOfContract(APIException):
    status_code = 403
    default_detail = "You are not in charge of this contract"
    default_code = "not_in_charge_of_contract"


class NotInChargeOfEvent(APIException):
    status_code = 403
    default_detail = "You are not in charge of this event"
    default_code = "not_in_charge_of_event"


class NotSalesMember(APIException):
    status_code = 403
    default_detail = "Please choose a Sales member for Sales contact field"
    default_code = "not_sales_member"


class NotSupportMember(APIException):
    status_code = 403
    default_detail = "Please choose a Support member for Support contact field"
    default_code = "not_sales_member"


class ContractMustBeSigned(APIException):
    status_code = 403
    default_detail = (
        "The contract associated to your client must be signed "
        "to create an event."
    )
    default_code = "contract_must_be_signed"


class EventOver(APIException):
    status_code = 403
    default_detail = "Event over. To update status, please contact Management."
    default_code = "event_over"


class ContractAlreadySigned(APIException):
    status_code = 403
    default_detail = (
        "Contract already signed. "
        "To change details, please sign a new contract. "
        "To terminate contract, please delete it."
    )
    default_code = "contract_already_signed"
