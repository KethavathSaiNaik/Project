export async function verifyClaim(claim) {
    const res = await fetch("http://127.0.0.1:8000/api/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ claim }),
    });

    if (!res.ok) throw new Error("Verification failed");
    return res.json();
}
