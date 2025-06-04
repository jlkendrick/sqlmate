"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";
import { Header } from "@/components/header";
import { authService } from "@/services/api";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { toast } from "@/components/ui/use-toast";

export default function ProfilePage() {
  const { user, loading, logout, isAuthenticated } = useAuth();
  const router = useRouter();
  const [showDeleteConfirmation, setShowDeleteConfirmation] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push("/login");
    }
  }, [loading, isAuthenticated, router]);

  if (loading) {
    return <p className="p-4 text-center">Loading profile…</p>;
  }

  if (!user) {
    return null; // This will redirect in the useEffect
  }

  const handleDeleteAccount = async () => {
    setIsDeleting(true);
    try {
      await authService.deleteUser();
      toast({
        title: "Account deleted",
        description: "Your account has been successfully deleted.",
      });
      logout(); // Log the user out after successful deletion
      router.push("/"); // Redirect to home page
    } catch (err: any) {
      
      toast({
        title: "Error",
        description: err.message || "Failed to delete account",
        variant: "destructive",
      });
      setIsDeleting(false); // Only reset if there was an error
    }
  };

  return (
    <div className="flex flex-col h-screen w-full">
      <Header />
      <div className="max-w-md mx-auto p-6 space-y-6 bg-card rounded-lg shadow mt-10">
        <h1 className="text-2xl font-semibold">Profile</h1>
        <div className="space-y-2">
          <p>
            <strong>Username:</strong> {user.username}
          </p>
          <p>
            <strong>Email:</strong> {user.email}
          </p>
        </div>
        <div className="flex flex-col space-y-4 pt-4">
          <Button variant="destructive" onClick={logout}>
            Logout
          </Button>
          <Button
            variant="outline"
            className="border-red-300 text-red-500 hover:bg-red-50 hover:text-red-600"
            onClick={() => setShowDeleteConfirmation(true)}
            disabled={isDeleting}
          >
            {isDeleting ? "Deleting..." : "Delete Account"}
          </Button>
        </div>

        <AlertDialog
          open={showDeleteConfirmation}
          onOpenChange={setShowDeleteConfirmation}
        >
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
              <AlertDialogDescription>
                This action cannot be undone. This will permanently delete your
                account and all data associated with it.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction
                onClick={handleDeleteAccount}
                className="bg-red-500 hover:bg-red-600"
              >
                Delete Account
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </div>
  );
}
