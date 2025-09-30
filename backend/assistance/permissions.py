"""
Custom permissions for the assistance module.

Implements role-based access control for assistance cases:
- Board members can create cases
- Fiscal Council members can approve/reject cases
- All authenticated users can view approved cases
"""

from rest_framework import permissions


class CanCreateCase(permissions.BasePermission):
    """
    Permission to create assistance cases.
    Only Board members and Admins can create cases.
    """
    message = "Apenas membros do Conselho Diretor podem criar casos de assistência."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Board and Admin can create
        return request.user.role in ['BOARD', 'SUPER_ADMIN']


class CanApproveCase(permissions.BasePermission):
    """
    Permission to approve/reject assistance cases.
    Only Fiscal Council members and Admins can approve.
    """
    message = "Apenas membros do Conselho Fiscal podem aprovar ou rejeitar casos."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Fiscal Council and Admin can approve
        return request.user.role in ['FISCAL_COUNCIL', 'SUPER_ADMIN']


class CanEditCase(permissions.BasePermission):
    """
    Permission to edit assistance cases.
    Only the creator or Admin can edit, and only if status allows.
    """
    message = "Você não tem permissão para editar este caso."

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin can always edit
        if request.user.role == 'SUPER_ADMIN':
            return True

        # Creator can edit their own cases if status allows
        if obj.created_by == request.user and obj.can_be_edited:
            return True

        return False


class CanViewInternalDescription(permissions.BasePermission):
    """
    Permission to view internal description of cases.
    Only Board, Fiscal Council, and Admin can see internal notes.
    """
    message = "Você não tem permissão para visualizar a descrição interna deste caso."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Board, Fiscal Council, and Admin can view internal descriptions
        return request.user.role in ['BOARD', 'FISCAL_COUNCIL', 'SUPER_ADMIN']
