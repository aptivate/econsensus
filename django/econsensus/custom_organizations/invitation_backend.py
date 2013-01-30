from organizations.backends.defaults import InvitationBackend

class CustomInvitationBackend(InvitationBackend):
    invitation_subject = 'email/invitation_subject.txt'
    invitation_body = 'email/invitation_body.html'
