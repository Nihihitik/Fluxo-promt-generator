import { User as UserIcon } from "lucide-react";
import { User } from "@/lib/api";

interface UserAvatarProps {
  user: User;
  size?: "sm" | "md" | "lg";
}

export function UserAvatar({ user, size = "md" }: UserAvatarProps) {
  const getInitials = (name?: string, email?: string) => {
    if (name) {
      return name
        .split(" ")
        .map((word) => word.charAt(0))
        .join("")
        .toUpperCase()
        .slice(0, 2);
    }
    if (email) {
      return email.charAt(0).toUpperCase();
    }
    return "U";
  };

  const sizeClasses = {
    sm: "h-8 w-8 text-xs",
    md: "h-10 w-10 text-sm",
    lg: "h-12 w-12 text-base",
  };

  const initials = getInitials(user.name, user.email);

  return (
    <div
      className={`${sizeClasses[size]} rounded-full bg-muted hover:bg-muted/80 border-2 border-border text-foreground flex items-center justify-center font-semibold transition-colors`}
    >
      {initials}
    </div>
  );
}