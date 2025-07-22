from fastapi import APIRouter

from backend.routes.admin import checkers
from backend.routes.admin import groups as admin_groups
from backend.routes.admin import users as admin_users
from backend.routes.sns_raise import instagram
from backend.routes.sns_raise import producers
from backend.routes.sns_raise import consumers
from backend.routes.sns_raise import unfollowers
from backend.routes.sns_raise import users
from backend.routes.sns_raise import groups
from backend.routes.sns_raise import verifications

api_router = APIRouter()
api_router.include_router(checkers.router, prefix="/admin/checkers", tags=["admin", "checkers"])
api_router.include_router(admin_groups.router, prefix="/admin/groups", tags=["admin", "groups"])
api_router.include_router(admin_users.router, prefix="/admin/users", tags=["admin", "users"])

api_router.include_router(instagram.router, prefix="/sns-raise/instagram", tags=["sns_raise", "instagram"])
api_router.include_router(producers.router, prefix="/sns-raise/producers", tags=["sns_raise", "producers"])
api_router.include_router(consumers.router, prefix="/sns-raise/consumers", tags=["sns_raise", "consumers"])
api_router.include_router(unfollowers.router, prefix="/sns-raise/unfollowers", tags=["sns_raise", "unfollowers"])
api_router.include_router(users.router, prefix="/sns-raise/users", tags=["sns_raise", "users"])
api_router.include_router(groups.router, prefix="/sns-raise/groups", tags=["sns_raise", "groups"])
api_router.include_router(verifications.router, prefix="/sns-raise/verifications", tags=["verifications"])
