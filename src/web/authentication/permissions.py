from rest_framework import permissions

class IsAccountOwner(permissions.BasePermission):
	"""
	Verify if user is the Account Owner
	"""
	def has_object_permission(self, request, view, obj):
		if request.user:
			return obj == request.user

		return False