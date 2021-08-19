from rest_framework.exceptions import APIException


class NoClientRegistered(APIException):
    status_code = 200
    default_detail = "No client registered"
    default_code = "no_client_registered"


class MissingCredentials(APIException):
    status_code = 403
    default_detail = (
        "Missing credentials: You cannot access " "the details of this page"
    )
    default_code = "missing_credentials"


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


class NoContractForClient(APIException):
    status_code = 403
    default_detail = "No existing contract for this client"
    default_code = "no_contract_for_client"


class ContractNotSigned(APIException):
    status_code = 403
    default_detail = "No signed contract for this client"
    default_code = "no_signed_contract"


class NotSalesMember(APIException):
    status_code = 403
    default_detail = "Please choose a Sales member for Sales contact field"
    default_code = "not_sales_member"


class NotSupportMember(APIException):
    status_code = 403
    default_detail = "Please choose a Support member for Support contact field"
    default_code = "not_sales_member"


class ContractAlreadyExists(APIException):
    status_code = 403
    default_detail = "A contract already exists with this client."
    default_code = "contract_already_exists"


class ContractMustBeSigned(APIException):
    status_code = 403
    default_detail = "The contract associated to your client must be signed " \
                     "to create an event."
    default_code = "contract_must_be_signed"


class EventOver(APIException):
    status_code = 403
    default_detail = "Event over. To update status, please contact Management."
    default_code = "event_over"


class ContractAlreadySigned(APIException):
    status_code = 403
    default_detail = "Contract already signed. To terminate contract, please delete it."
    default_code = "contract_already_signed"


class ClientNotFound(APIException):
    status_code = 404
    default_detail = "Client not found"
    default_code = "client_not_found"


class ContractNotFound(APIException):
    status_code = 404
    default_detail = "Contract not found"
    default_code = "contract_not_found"


class EventNotFound(APIException):
    status_code = 404
    default_detail = "Event not found"
    default_code = "event_not_found"
