from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app.models.role import Role
from app.models.menu import Menu
from app.models.dictionary import Dictionary
from app.models.announcement import Announcement
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def require_admin(f):
    """需要管理员权限的装饰器"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        user_model = User()
        user = user_model.get_user_by_id(current_user.id)
        if not user or user.get('role') not in ['super_admin', 'admin']:
            return jsonify({
                'code': 403,
                'msg': '权限不足'
            }), 403
        return f(*args, **kwargs)
    return decorated_function

def require_super_admin(f):
    """需要超级管理员权限的装饰器"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        user_model = User()
        user = user_model.get_user_by_id(current_user.id)
        if not user or user.get('role') != 'super_admin':
            return jsonify({
                'code': 403,
                'msg': '需要超级管理员权限'
            }), 403
        return f(*args, **kwargs)
    return decorated_function

# 角色管理
@admin_bp.route('/roles', methods=['GET'])
@require_admin
def get_roles():
    """获取角色列表"""
    try:
        role_model = Role()
        roles = role_model.get_all_roles()
        return jsonify({
            'code': 0,
            'data': roles,
            'msg': '获取成功'
        })
    except Exception as e:
        logger.error(f"获取角色列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '获取角色列表失败'
        }), 500

@admin_bp.route('/roles', methods=['POST'])
@require_super_admin
def create_role():
    """创建角色"""
    try:
        data = request.get_json()
        role_model = Role()
        
        # 检查角色代码是否已存在
        if role_model.get_role_by_code(data.get('code')):
            return jsonify({
                'code': 400,
                'msg': '角色代码已存在'
            }), 400
        
        role = role_model.create_role(data)
        return jsonify({
            'code': 0,
            'data': role,
            'msg': '创建成功'
        })
    except Exception as e:
        logger.error(f"创建角色失败: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '创建角色失败'
        }), 500

@admin_bp.route('/roles/<role_id>', methods=['PUT'])
@require_super_admin
def update_role(role_id):
    """更新角色"""
    try:
        data = request.get_json()
        role_model = Role()
        
        if role_model.update_role(role_id, data):
            return jsonify({
                'code': 0,
                'msg': '更新成功'
            })
        else:
            return jsonify({
                'code': 400,
                'msg': '更新失败'
            }), 400
    except Exception as e:
        logger.error(f"更新角色失败: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '更新角色失败'
        }), 500

@admin_bp.route('/roles/<role_id>', methods=['DELETE'])
@require_super_admin
def delete_role(role_id):
    """删除角色"""
    try:
        role_model = Role()
        
        # 检查是否为系统默认角色
        role = role_model.collection.find_one({"_id": ObjectId(role_id)})
        if role and role.get('code') in ['super_admin', 'admin', 'member', 'user']:
            return jsonify({
                'code': 400,
                'msg': '系统默认角色不能删除'
            }), 400
        
        if role_model.delete_role(role_id):
            return jsonify({
                'code': 0,
                'msg': '删除成功'
            })
        else:
            return jsonify({
                'code': 400,
                'msg': '删除失败'
            }), 400
    except Exception as e:
        logger.error(f"删除角色失败: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '删除角色失败'
        }), 500

# 菜单管理
@admin_bp.route('/menus', methods=['GET'])
@require_admin
def get_menus():
    """获取菜单树"""
    try:
        menu_model = Menu()
        menus = menu_model.get_menu_tree()
        return jsonify({
            'code': 0,
            'data': menus,
            'msg': '获取成功'
        })
    except Exception as e:
        logger.error(f"获取菜单失败: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '获取菜单失败'
        }), 500

@admin_bp.route('/menus/user', methods=['GET'])
@login_required
def get_user_menus():
    """获取当前用户的菜单"""
    try:
        user_model = User()
        user = user_model.get_user_by_id(current_user.id)
        role_code = user.get('role', 'user')
        
        menu_model = Menu()
        menus = menu_model.get_menus_by_role(role_code)
        return jsonify({
            'code': 0,
            'data': menus,
            'msg': '获取成功'
        })
    except Exception as e:
        logger.error(f"获取用户菜单失败: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '获取用户菜单失败'
        }), 500

@admin_bp.route('/menus', methods=['POST'])
@require_super_admin
def create_menu():
    """创建菜单"""
    try:
        data = request.get_json()
        menu_model = Menu()
        menu = menu_model.create_menu(data)
        return jsonify({
            'code': 0,
            'data': menu,
            'msg': '创建成功'
        })
    except Exception as e:
        logger.error(f"创建菜单失败: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '创建菜单失败'
        }), 500

@admin_bp.route('/menus/<menu_id>', methods=['PUT'])
@require_super_admin
def update_menu(menu_id):
    """更新菜单"""
    try:
        data = request.get_json()
        menu_model = Menu()
        
        if menu_model.update_menu(menu_id, data):
            return jsonify({
                'code': 0,
                'msg': '更新成功'
            })
        else:
            return jsonify({
                'code': 400,
                'msg': '更新失败'
            }), 400
    except Exception as e:
        logger.error(f"更新菜单失败: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '更新菜单失败'
        }), 500

@admin_bp.route('/menus/<menu_id>', methods=['DELETE'])
@require_super_admin
def delete_menu(menu_id):
    """删除菜单"""
    try:
        menu_model = Menu()
        success, msg = menu_model.delete_menu(menu_id)
        
        if success:
            return jsonify({
                'code': 0,
                'msg': msg
            })
        else:
            return jsonify({
                'code': 400,
                'msg': msg
            }), 400
    except Exception as e:
        logger.error(f"删除菜单失败: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '删除菜单失败'
        }), 500

# 字典管理
@admin_bp.route('/dictionaries', methods=['GET'])
@require_admin
def get_dictionaries():
    """获取字典类型列表"""
    try:
        dict_model = Dictionary()
        dicts = dict_model.get_all_dict_types()
        return jsonify({
            'code': 0,
            'data': dicts,
            'msg': '获取成功'
        })
    except Exception as e:
        logger.error(f"获取字典列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '获取字典列表失败'
        }), 500

@admin_bp.route('/dictionaries/<code>', methods=['GET'])
def get_dictionary_by_code(code):
    """根据代码获取字典详情"""
    try:
        dict_model = Dictionary()
        dict_data = dict_model.get_dict_by_code(code)
        
        if dict_data:
            return jsonify({
                'code': 0,
                'data': dict_data,
                'msg': '获取成功'
            })
        else:
            return jsonify({
                'code': 404,
                'msg': '字典不存在'
            }), 404
    except Exception as e:
        logger.error(f"获取字典详情失败: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '获取字典详情失败'
        }), 500

@admin_bp.route('/dictionaries', methods=['POST'])
@require_super_admin
def create_dictionary():
    """创建字典类型"""
    try:
        data = request.get_json()
        dict_model = Dictionary()
        
        # 检查代码是否已存在
        if dict_model.get_dict_by_code(data.get('code')):
            return jsonify({
                'code': 400,
                'msg': '字典代码已存在'
            }), 400
        
        dict_type = dict_model.create_dict_type(data)
        return jsonify({
            'code': 0,
            'data': dict_type,
            'msg': '创建成功'
        })
    except Exception as e:
        logger.error(f"创建字典失败: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '创建字典失败'
        }), 500

@admin_bp.route('/dictionaries/<type_code>/items', methods=['POST'])
@require_super_admin
def create_dict_item(type_code):
    """创建字典项"""
    try:
        data = request.get_json()
        dict_model = Dictionary()
        
        # 检查字典类型是否存在
        if not dict_model.get_dict_by_code(type_code):
            return jsonify({
                'code': 404,
                'msg': '字典类型不存在'
            }), 404
        
        dict_item = dict_model.create_dict_item(type_code, data)
        return jsonify({
            'code': 0,
            'data': dict_item,
            'msg': '创建成功'
        })
    except Exception as e:
        logger.error(f"创建字典项失败: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '创建字典项失败'
        }), 500

# 公告管理
@admin_bp.route('/announcements', methods=['GET'])
@require_admin
def get_announcements():
    """获取公告列表"""
    try:
        announcement_model = Announcement()
        announcements = announcement_model.get_active_announcements()
        return jsonify({
            'code': 0,
            'data': announcements,
            'msg': '获取成功'
        })
    except Exception as e:
        logger.error(f"获取公告列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '获取公告列表失败'
        }), 500

@admin_bp.route('/announcements', methods=['POST'])
@require_admin
def create_announcement():
    """创建公告"""
    try:
        data = request.get_json()
        data['created_by'] = current_user.id
        
        announcement_model = Announcement()
        announcement = announcement_model.create_announcement(data)
        return jsonify({
            'code': 0,
            'data': announcement,
            'msg': '创建成功'
        })
    except Exception as e:
        logger.error(f"创建公告失败: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '创建公告失败'
        }), 500

# 初始化默认数据
@admin_bp.route('/init', methods=['POST'])
@require_super_admin
def init_default_data():
    """初始化默认数据"""
    try:
        # 初始化角色
        role_model = Role()
        role_model.init_default_roles()
        
        # 初始化菜单
        menu_model = Menu()
        menu_model.init_default_menus()
        
        return jsonify({
            'code': 0,
            'msg': '初始化成功'
        })
    except Exception as e:
        logger.error(f"初始化默认数据失败: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '初始化失败'
        }), 500 