#include "CoreMinimal.h"
#include "GameFramework/Actor.h"

// ❌ Clasa nu are prefix "A" (Actor class ar trebui să fie AMyBadActor)
class MyBadActor : public AActor
{
public:
    // ❌ Variabila nu respectă PascalCase (ar trebui HealthPoints)
    float health_points;

    // ❌ Boolean fără prefix b (ar trebui bIsAlive)
    bool IsAlive;

    // ❌ Funcția nu e PascalCase (ar trebui TakeDamage)
    void take_damage(float damageAmount)
    {
        // ❌ Variabilă locală în PascalCase (ar trebui camelCase)
        bool isAlive;
        float NewHealth = health_points - damageAmount;
        IsAlive = (NewHealth > 0);
    }
};

