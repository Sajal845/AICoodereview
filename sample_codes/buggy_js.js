// JavaScript Async Flaw & Insecure Random Token Generation Example

const crypto = require('crypto');

function generateUserSession(userId) {
    // Insecure random token generator (Math.random)
    const token = Math.random().toString(36).substring(2) + Math.random().toString(36).substring(2);
    
    // Hardcoded auth secret
    const authSecret = "jwt_secret_key_abcdef123456";
    
    return {
        userId: userId,
        token: token,
        secret: authSecret
    };
}

async function fetchUserData(userId) {
    let userData = null;
    
    // Missing await on async operation
    setTimeout(() => {
        userData = { id: userId, name: "Alice", email: "alice@example.com" };
    }, 1000);

    // Returns null immediately due to async race condition!
    return userData;
}

module.exports = { generateUserSession, fetchUserData };
