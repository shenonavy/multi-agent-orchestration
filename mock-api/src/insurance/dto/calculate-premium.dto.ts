import { IsString, IsNumber } from 'class-validator';

export class CalculatePremiumDto {
  @IsString()
  policy_id: string;

  @IsNumber()
  current_coverage: number;

  @IsNumber()
  new_coverage: number;
}
