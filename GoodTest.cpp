#include "CoreMinimal.h"
#include "GameFramework/Actor.h"

// ✅ Clasa are prefix "A"
class AMyGoodActor : public AActor
{
public:
    // ✅ Variabilă membră în PascalCase
    float HealthPoints;

    // ✅ Boolean cu prefix b
    bool bIsAlive;

    // ✅ Funcția în PascalCase
    void TakeDamage(float damageAmount)
    {
        // ✅ Variabile locale în camelCase
        float newHealth = HealthPoints - damageAmount;
        bool bShouldDie = newHealth <= 0.0f;

        HealthPoints = newHealth;
        bIsAlive = !bShouldDie;
    }
};
