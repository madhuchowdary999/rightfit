import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RightFit",
  description: "Job-specific candidate skill verification for recruiters",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
