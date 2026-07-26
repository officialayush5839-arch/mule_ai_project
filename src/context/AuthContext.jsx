import React, { createContext, useState } from 'react';

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // Temporary mock user for Hackathon / Development
  // In a real scenario, this would be initialized via JWT/OAuth state
  const [user] = useState({
    id: "admin-001",
    name: "Ayush S.",
    role: "ADMIN", 
    initials: "AS",
    title: "Lead Analyst"
  });

  return (
    <AuthContext.Provider value={{ user }}>
      {children}
    </AuthContext.Provider>
  );
}
