import { IsString, IsArray, IsOptional } from 'class-validator';

export class CreateClaimDto {
  @IsString()
  policy_id: string;

  @IsString()
  damage_description: string;

  @IsString()
  vehicle: string;

  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  photos?: string[];
}
