import { Module } from '@nestjs/common';
import { InsuranceModule } from './insurance/insurance.module';
import { HealthController } from './health.controller';

@Module({
  imports: [InsuranceModule],
  controllers: [HealthController],
})
export class AppModule {}
