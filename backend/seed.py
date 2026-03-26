import json
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import SessionLocal
from app.models.user import User, Role
from app.models.post import Post, Category, Tag
from app.core.security import get_password_hash

def seed_db():
    db = SessionLocal()
    
    # 1. Create categories
    cat_names = ["前端开发", "后端架构", "运维部署", "UI设计", "人工智能"]
    categories = []
    for name in cat_names:
        cat = db.query(Category).filter(Category.name == name).first()
        if not cat:
            cat = Category(name=name, description=f"{name}相关技术文章")
            db.add(cat)
            db.commit()
            db.refresh(cat)
        categories.append(cat)
        
    # 2. Create tags
    tag_names = ["Vue3", "React", "JavaScript", "Tailwind CSS", "Python", "FastAPI", "Docker", "Figma", "Machine Learning", "TypeScript"]
    tags = []
    for name in tag_names:
        tag = db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        tags.append(tag)

    # 3. Ensure a user exists
    user = db.query(User).filter(User.username == "admin").first()
    if not user:
        role = db.query(Role).filter(Role.name == "admin").first()
        if not role:
            role = Role(name="admin", permissions="all")
            db.add(role)
            db.commit()
            db.refresh(role)
            
        user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("123456"),
            role_id=role.id,
            bio="系统管理员，技术爱好者。"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    try:
        # 4. Create 12 mock posts
        # Note: Do not delete existing tags or categories here, just the posts and post_tags
        db.execute(text("DELETE FROM post_tags"))
        db.execute(text("DELETE FROM posts"))
        db.commit()
        
        # We don't delete tags, just reuse them
        
        mock_titles = [
            "Vue3 Composition API 最佳实践指南",
            "Tailwind CSS：为什么它是现代前端的必选项？",
            "FastAPI 快速入门：构建高性能 Python 后端",
            "Docker 容器化部署完全指南",
            "2024年 UI/UX 设计趋势前瞻",
            "深入理解 JavaScript 闭包与作用域链",
            "React Server Components 深度解析",
            "大模型时代：如何入门机器学习？",
            "TypeScript 高级类型技巧解析",
            "前端性能优化：从加载到渲染的全面指南",
            "微服务架构下的 API 网关设计",
            "如何打造一个优雅的现代化博客系统"
        ]
        
        mock_covers = [
            "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800&q=80",
            "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=800&q=80",
            "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800&q=80",
            "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80",
            "https://images.unsplash.com/photo-1522542550221-31fd19575a2d?w=800&q=80",
            "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=800&q=80"
        ]
    
        for i in range(12):
            post = Post(
                title=mock_titles[i % len(mock_titles)] + (f" (Part {i//len(mock_titles) + 1})" if i >= len(mock_titles) else ""),
                content="> 这是一个系统自动生成的示例博客摘要内容。在这里我们将深入探讨相关的技术细节、实现原理以及在实际项目中的最佳实践。本文包含丰富的代码示例和架构解析...\n\n### 1. 引言\n技术的发展日新月异，掌握核心原理才能在变化中立于不败之地...",
                cover_image=random.choice(mock_covers),
                author_id=user.id,
                category_id=random.choice(categories).id,
                views=random.randint(100, 10000),
                likes=random.randint(10, 500),
                status="published",
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            
            # Add 2-3 random unique tags
            post_tags = random.sample(tags, random.randint(2, 3))
            
            # Use a separate query to fetch tags by ID to ensure they're bound to current session
            bound_tags = []
            for t in post_tags:
                tag_in_db = db.query(Tag).filter(Tag.id == t.id).first()
                if tag_in_db:
                    bound_tags.append(tag_in_db)
            
            # Use append to avoid identity set errors
            for t in bound_tags:
                if t not in post.tags:
                    post.tags.append(t)
            
            db.add(post)
            db.commit() # Commit each post immediately
            db.refresh(post) # Ensure it's fully flushed to db
        
    except Exception as e:
        print(f"Error seeding posts: {e}")
        db.rollback()
    finally:
        print("Successfully seeded 12 mock posts!")
        
    db.close()

if __name__ == "__main__":
    seed_db()
